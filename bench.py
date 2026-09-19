"""Manual benchmark for the university-registration corpus.

Run: python bench.py
     python bench.py --chunker recursive
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from main import parse_front_matter
from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import GeminiEmbedder, LocalEmbedder, OpenAIEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).parent
CORPUS_DIR = PROJECT_DIR / "data" / "university_services"
CACHE_PATH = PROJECT_DIR / ".cache" / "embedding_cache.json"
AGENT_CACHE_PATH = PROJECT_DIR / ".cache" / "agent_answer_cache.json"

# Exactly five shared queries.  Gold answers were copied from the cited source files.
BENCHMARKS = [
    {
        "query": "How many units make an undergraduate student full time?",
        "gold_doc_id": "course-registration",
        "gold_answer": "36 or more units.",
        "metadata_filter": None,
    },
    {
        "query": "What must a student do to request a course-time conflict?",
        "gold_doc_id": "course-registration",
        "gold_answer": "Submit the request in SIO; the advisor and instructors approve; the student accepts conditions.",
        "metadata_filter": None,
    },
    {
        "query": "What happens on the transcript after a course withdrawal?",
        "gold_doc_id": "course-changes",
        "gold_answer": "A W grade appears.",
        "metadata_filter": None,
    },
    {
        "query": "How are undergraduate registration start times assigned?",
        "gold_doc_id": "registration-start-times",
        "gold_answer": "Randomly from the last three ID-card digits, rotating through four time blocks.",
        "metadata_filter": {"audience": "student"},
    },
    {
        "query": "When must a non-degree staff member submit a petition, and can they receive drop vouchers?",
        "gold_doc_id": "staff-non-degree-registration",
        "gold_answer": "By the first day of classes; no Drop Vouchers.",
        "metadata_filter": None,
    },
]

SIMILARITY_PAIRS = [
    (
        "Students submit a Course Time Conflict Request through SIO.",
        "To enroll in overlapping classes, a student files a time-conflict request in SIO.",
        "cao",
    ),
    (
        "Undergraduate students may use three vouchers during their career.",
        "First-year undergraduate students register on Friday.",
        "trung bình",
    ),
    (
        "Registration start times are shown on the SIO Registration page.",
        "Students should consult their academic advisor before using a voucher.",
        "thấp",
    ),
    (
        "Faculty must submit a non-degree petition by the first day of classes.",
        "Staff must submit a non-degree petition by the first day of classes.",
        "cao",
    ),
    (
        "Dropped courses before the add/drop deadline do not appear on the transcript.",
        "A course withdrawal produces a W grade on the transcript.",
        "trung bình",
    ),
]


def get_chunker(name: str):
    """The only strategy switch: keep ingestion and search identical for comparison."""
    return {
        "heading": HeadingChunker(chunk_size=500),
        "fixed": FixedSizeChunker(chunk_size=500, overlap=50),
        "sentence": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=500),
    }[name]


class CachedEmbedder:
    """Cache embeddings by content hash so rerunning OpenAI benchmark costs less."""

    def __init__(self, embedder, cache_path: Path = CACHE_PATH) -> None:
        self.embedder = embedder
        self.cache_path = cache_path
        self.cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        self._backend_name = getattr(embedder, "_backend_name", type(embedder).__name__)

    def __call__(self, text: str) -> list[float]:
        key = hashlib.sha256(f"{self._backend_name}:{text}".encode("utf-8")).hexdigest()
        if key not in self.cache:
            self.cache[key] = self.embedder(text)
            self.cache_path.parent.mkdir(exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")
        return self.cache[key]


def get_embedder(provider: str):
    load_dotenv(override=False)
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is missing. Put it in .env or set it in PowerShell before running.")
        return CachedEmbedder(OpenAIEmbedder())
    if provider == "local":
        return LocalEmbedder()
    if provider == "gemini":
        return CachedEmbedder(GeminiEmbedder())
    return _mock_embed


def get_openai_llm():
    """Return a small grounded-answer LLM function, cached by the full prompt."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. The agent answer cannot be generated.")
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    cache = json.loads(AGENT_CACHE_PATH.read_text(encoding="utf-8")) if AGENT_CACHE_PATH.exists() else {}

    def llm_fn(prompt: str) -> str:
        key = hashlib.sha256(f"{model}:{prompt}".encode("utf-8")).hexdigest()
        if key not in cache:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            cache[key] = response.choices[0].message.content or ""
            AGENT_CACHE_PATH.parent.mkdir(exist_ok=True)
            AGENT_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        return cache[key]

    return llm_fn


class FilteredStoreView:
    """Lets KnowledgeBaseAgent use the same pre-filtered candidates as the benchmark."""

    def __init__(self, store: EmbeddingStore, metadata_filter: dict | None) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.store.search_with_filter(query, top_k=top_k, metadata_filter=self.metadata_filter)


def load_corpus(chunker_name: str) -> list[Document]:
    chunker = get_chunker(chunker_name)
    documents: list[Document] = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        frontmatter, content = parse_front_matter(path.read_text(encoding="utf-8"))
        parent_doc_id = frontmatter.get("doc_id", path.stem)
        for index, chunk in enumerate(chunker.chunk(content)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={
                        **frontmatter,
                        "doc_id": parent_doc_id,
                        "source_file": str(path.relative_to(PROJECT_DIR)),
                        "chunk_index": index,
                        "chunking_strategy": chunker_name,
                    },
                )
            )
    return documents


def run(chunker_name: str, provider: str, filter_mode: str = "on", with_agent: bool = False) -> None:
    docs = load_corpus(chunker_name)
    embedder = get_embedder(provider)
    store = EmbeddingStore("university_registration_benchmark", embedding_fn=embedder)
    store.add_documents(docs)
    print(f"Chunker: {chunker_name}; files: 9; chunks stored: {store.get_collection_size()}")
    print(f"Embedding: {getattr(embedder, '_backend_name', type(embedder).__name__)}")
    llm_fn = get_openai_llm() if with_agent else None

    for number, benchmark in enumerate(BENCHMARKS, start=1):
        metadata_filter = benchmark["metadata_filter"] if filter_mode == "on" else None
        results = store.search_with_filter(
            benchmark["query"], top_k=3, metadata_filter=metadata_filter
        )
        print(f"\n[{number}] {benchmark['query']}")
        print(f"Gold: {benchmark['gold_answer']} (doc_id={benchmark['gold_doc_id']})")
        print(f"Filter: {metadata_filter or 'none'}")
        for rank, result in enumerate(results, start=1):
            preview = result["content"].replace("\n", " ")[:180]
            print(f"  {rank}. score={result['score']:.3f} doc_id={result['metadata']['doc_id']} :: {preview}...")
        if llm_fn:
            agent = KnowledgeBaseAgent(FilteredStoreView(store, metadata_filter), llm_fn)
            print(f"Agent answer: {agent.answer(benchmark['query'], top_k=3)}")


def print_baseline() -> None:
    """Compare the three supplied chunkers on bodies only (never front matter)."""
    comparator = ChunkingStrategyComparator()
    print("Baseline (front matter removed; chunk_size=200)")
    for path in sorted(CORPUS_DIR.glob("*.md"))[:3]:
        _, content = parse_front_matter(path.read_text(encoding="utf-8"))
        result = comparator.compare(content, chunk_size=200)
        values = ", ".join(
            f"{name}: count={value['count']}, avg_length={value['avg_length']:.1f}"
            for name, value in result.items()
        )
        print(f"{path.stem}: {values}")


def print_similarity_pairs(provider: str) -> None:
    from src.chunking import compute_similarity

    embedder = get_embedder(provider)
    print(f"Similarity embedding: {getattr(embedder, '_backend_name', type(embedder).__name__)}")
    for number, (sentence_a, sentence_b, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        print(f"{number}. prediction={prediction}; score={score:.3f}")
        print(f"   A: {sentence_a}")
        print(f"   B: {sentence_b}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the five university-services benchmark queries.")
    parser.add_argument("--chunker", choices=["heading", "fixed", "sentence", "recursive"], default="fixed")
    parser.add_argument("--provider", choices=["openai", "local", "gemini", "mock"], default="openai")
    parser.add_argument(
        "--filter-mode",
        choices=["on", "off"],
        default="on",
        help="Use metadata filters from the benchmark (on) or disable them for A/B comparison (off).",
    )
    parser.add_argument("--baseline", action="store_true", help="Print baseline for the first three files, then exit.")
    parser.add_argument("--similarity", action="store_true", help="Print five individual cosine-similarity measurements.")
    parser.add_argument("--with-agent", action="store_true", help="Generate grounded OpenAI agent answers for the five queries.")
    args = parser.parse_args()
    if args.baseline:
        print_baseline()
    elif args.similarity:
        print_similarity_pairs(args.provider)
    else:
        run(args.chunker, args.provider, args.filter_mode, args.with_agent)


if __name__ == "__main__":
    main()

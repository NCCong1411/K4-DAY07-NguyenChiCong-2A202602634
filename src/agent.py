from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "I could not find relevant context to answer this question."

        context = "\n\n".join(
            f"[{index}] Source: {result['metadata'].get('doc_id', result['id'])}\n{result['content']}"
            for index, result in enumerate(results, start=1)
        )
        prompt = (
            "Answer using only the context below. Cite the supporting source number "
            "in square brackets, for example [1]. If the context does not contain "
            "the answer, say that you could not find it in the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)

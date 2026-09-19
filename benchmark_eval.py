"""Content-aware checks for the five shared Lab 7 benchmark questions.

The phrases come from the saved corpus, not from the Vietnamese gold-answer
paraphrases. All phrases for a question must occur in retrieved gold-document
chunks; a matching doc_id alone is insufficient.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


ANSWER_PHRASES: dict[int, tuple[str, ...]] = {
    1: (
        "Course Time Conflict Request",
        "advisor will either approve or deny",
        "instructors of the conflicting course sections",
        "conditions are accepted",
    ),
    2: ("first-years register on Friday",),
    3: (
        "primary academic advisor",
        "Student Services Suite (S3)",
        "within 24 hours",
    ),
    4: ("three vouchers", "one voucher per semester"),
    5: (
        "last three digits",
        "Students may register any time after their assigned registration start time",
    ),
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).casefold()


def evaluate_results(number: int, gold_doc_id: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate whether top-3 contains the full answer-bearing gold context."""
    phrases = ANSWER_PHRASES[number]
    gold_hits = [
        (rank, result)
        for rank, result in enumerate(results, 1)
        if result["metadata"].get("doc_id") == gold_doc_id
    ]
    gold_rank = gold_hits[0][0] if gold_hits else None
    gold_context = _normalize(" ".join(result["content"] for _, result in gold_hits))
    found = [phrase for phrase in phrases if _normalize(phrase) in gold_context]
    missing = [phrase for phrase in phrases if phrase not in found]
    answer_in_context = bool(gold_hits) and not missing
    points = 2 if answer_in_context and gold_rank == 1 else 1 if answer_in_context else 0
    return {
        "doc_hit": bool(gold_hits),
        "gold_rank": gold_rank,
        "found_phrases": found,
        "missing_phrases": missing,
        "answer_in_context": answer_in_context,
        "retrieval_points": points,
    }

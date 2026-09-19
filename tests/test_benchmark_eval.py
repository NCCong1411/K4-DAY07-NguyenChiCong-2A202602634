from benchmark_eval import evaluate_results


def result(doc_id: str, content: str) -> dict:
    return {"metadata": {"doc_id": doc_id}, "content": content}


def test_gold_document_without_answer_scores_zero() -> None:
    evaluation = evaluate_results(4, "course-changes", [result("course-changes", "Drop deadline and tuition")])
    assert evaluation["doc_hit"] is True
    assert evaluation["answer_in_context"] is False
    assert evaluation["retrieval_points"] == 0


def test_answer_can_span_two_retrieved_gold_chunks() -> None:
    evaluation = evaluate_results(
        4,
        "course-changes",
        [
            result("other", "Unrelated"),
            result("course-changes", "Undergraduates have three vouchers."),
            result("course-changes", "They may use one voucher per semester."),
        ],
    )
    assert evaluation["gold_rank"] == 2
    assert evaluation["answer_in_context"] is True
    assert evaluation["retrieval_points"] == 1

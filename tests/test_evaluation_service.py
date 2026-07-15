import json
from pathlib import Path

from banking_rag.core.schemas import RetrievedChunk
from banking_rag.services.evaluation_service import RetrievalEvaluationService


class FakeRetriever:
    """Fake retriever for deterministic evaluation tests."""

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        if "password" in query.lower():
            return [
                RetrievedChunk(
                    text="Customers can reset their mobile banking password.",
                    source="mobile_app_access.md",
                    section="Password Recovery",
                    chunk_index=0,
                    distance=0.2,
                    metadata={},
                )
            ]

        return [
            RetrievedChunk(
                text="General payment safety guidance.",
                source="digital_payments.md",
                section="Payment Safety",
                chunk_index=0,
                distance=0.2,
                metadata={},
            ),
            RetrievedChunk(
                text="Customers may raise a QR payment dispute.",
                source="digital_payments.md",
                section="QR Payment Disputes",
                chunk_index=1,
                distance=0.3,
                metadata={},
            ),
        ]


def test_evaluation_service_tracks_top_1_and_top_k_pass(
    tmp_path: Path,
) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "How do I reset my password?",
                    "expected_top_source": "mobile_app_access.md",
                    "expected_top_section": "Password Recovery",
                    "expected_behavior": "Mention password recovery.",
                    "expected_answer_type": "direct_answer",
                    "must_not_include": [],
                },
                {
                    "question": "What should happen if my QR payment failed?",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Mention QR dispute.",
                    "expected_answer_type": "direct_answer",
                    "must_not_include": [],
                },
            ]
        ),
        encoding="utf-8",
    )

    service = RetrievalEvaluationService(
        retriever=FakeRetriever(),  # type: ignore[arg-type]
        evaluation_file=evaluation_file,
    )

    summary = service.run(top_k=2)

    assert summary.total == 2
    assert summary.top_1_passed == 1
    assert summary.top_k_passed == 2
    assert summary.failed_top_k == 0

    assert summary.results[0].expected_rank == 1
    assert summary.results[0].top_1_passed is True
    assert summary.results[0].top_k_passed is True

    assert summary.results[1].expected_rank == 2
    assert summary.results[1].top_1_passed is False
    assert summary.results[1].top_k_passed is True


def test_evaluation_service_fails_when_expected_chunk_not_in_top_k(
    tmp_path: Path,
) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "How do I reset my password?",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Wrong expectation for test.",
                    "expected_answer_type": "direct_answer",
                    "must_not_include": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    service = RetrievalEvaluationService(
        retriever=FakeRetriever(),  # type: ignore[arg-type]
        evaluation_file=evaluation_file,
    )

    summary = service.run(top_k=1)

    assert summary.total == 1
    assert summary.top_1_passed == 0
    assert summary.top_k_passed == 0
    assert summary.failed_top_k == 1
    assert summary.results[0].passed is False


def test_evaluation_service_loads_no_answer_metadata(
    tmp_path: Path,
) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "What is the exact refund timeline?",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Say not enough information.",
                    "expected_answer_type": "no_answer",
                    "must_not_include": ["24 hours", "3 days"],
                }
            ]
        ),
        encoding="utf-8",
    )

    service = RetrievalEvaluationService(
        retriever=FakeRetriever(),  # type: ignore[arg-type]
        evaluation_file=evaluation_file,
    )

    question = service.load_questions()[0]

    assert question.expected_answer_type == "no_answer"
    assert "24 hours" in question.must_not_include
    assert "3 days" in question.must_not_include
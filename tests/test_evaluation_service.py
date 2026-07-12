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
                text="Customers may raise a QR payment dispute.",
                source="digital_payments.md",
                section="QR Payment Disputes",
                chunk_index=0,
                distance=0.3,
                metadata={},
            )
        ]


def test_evaluation_service_passes_matching_top_result(tmp_path: Path) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "How do I reset my password?",
                    "expected_top_source": "mobile_app_access.md",
                    "expected_top_section": "Password Recovery",
                    "expected_behavior": "Mention password recovery.",
                }
            ]
        ),
        encoding="utf-8",
    )

    service = RetrievalEvaluationService(
        retriever=FakeRetriever(),  # type: ignore[arg-type]
        evaluation_file=evaluation_file,
    )

    summary = service.run()

    assert summary.total == 1
    assert summary.passed == 1
    assert summary.failed == 0
    assert summary.results[0].passed is True


def test_evaluation_service_fails_mismatched_top_result(tmp_path: Path) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "How do I reset my password?",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Wrong expectation for test.",
                }
            ]
        ),
        encoding="utf-8",
    )

    service = RetrievalEvaluationService(
        retriever=FakeRetriever(),  # type: ignore[arg-type]
        evaluation_file=evaluation_file,
    )

    summary = service.run()

    assert summary.total == 1
    assert summary.passed == 0
    assert summary.failed == 1
    assert summary.results[0].passed is False
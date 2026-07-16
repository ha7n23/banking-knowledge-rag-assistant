import json
from pathlib import Path

from banking_rag.core.schemas import (
    RAGAnswer,
    SourceReference,
)
from banking_rag.services.answer_evaluation_service import (
    AnswerEvaluationService,
)


class FakeSafeAnswerService:
    """Fake answer service that returns safe answers."""

    def answer(self, *args, **kwargs) -> RAGAnswer:
        question = kwargs.get("question", "")

        return RAGAnswer(
            question=question,
            answer=(
                "The provided documents do not contain enough information "
                "to specify an exact refund timeline."
            ),
            sources=[
                SourceReference(
                    source="digital_payments.md",
                    section="QR Payment Disputes",
                    chunk_index=0,
                    distance=0.42,
                )
            ],
            retrieved_chunks=[],
        )


class FakeUnsafeAnswerService:
    """Fake answer service that returns unsupported claims."""

    def answer(self, *args, **kwargs) -> RAGAnswer:
        question = kwargs.get("question", "")

        return RAGAnswer(
            question=question,
            answer="The refund will happen within 3 days.",
            sources=[
                SourceReference(
                    source="digital_payments.md",
                    section="QR Payment Disputes",
                    chunk_index=0,
                    distance=0.42,
                )
            ],
            retrieved_chunks=[],
        )


class FakeNoSourceAnswerService:
    """Fake answer service that returns an answer without sources."""

    def answer(self, *args, **kwargs) -> RAGAnswer:
        question = kwargs.get("question", "")

        return RAGAnswer(
            question=question,
            answer="Customers may raise a dispute.",
            sources=[],
            retrieved_chunks=[],
        )


def test_answer_evaluation_passes_safe_no_answer(
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

    service = AnswerEvaluationService(
        answer_service=FakeSafeAnswerService(),
        evaluation_file=evaluation_file,
    )

    summary = service.run()

    assert summary.total == 1
    assert summary.passed == 1
    assert summary.failed == 0
    assert summary.results[0].passed is True
    assert summary.results[0].no_answer_language_detected is True


def test_answer_evaluation_fails_forbidden_term(
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

    service = AnswerEvaluationService(
        answer_service=FakeUnsafeAnswerService(),
        evaluation_file=evaluation_file,
    )

    summary = service.run()

    assert summary.total == 1
    assert summary.passed == 0
    assert summary.failed == 1
    assert summary.results[0].forbidden_terms_found == ["3 days"]


def test_answer_evaluation_fails_when_sources_missing(
    tmp_path: Path,
) -> None:
    evaluation_file = tmp_path / "eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "Can I raise a dispute?",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Mention dispute process.",
                    "expected_answer_type": "direct_answer",
                    "must_not_include": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    service = AnswerEvaluationService(
        answer_service=FakeNoSourceAnswerService(),
        evaluation_file=evaluation_file,
    )

    summary = service.run()

    assert summary.total == 1
    assert summary.passed == 0
    assert summary.failed == 1
    assert summary.results[0].has_sources is False
import json
from pathlib import Path

from banking_rag.core.schemas import (
    AnswerEvaluationResult,
    AnswerEvaluationSummary,
)
from banking_rag.services.evaluation_report_writer import (
    AnswerEvaluationReportWriter,
)


def test_answer_evaluation_report_writer_creates_json_and_markdown(
    tmp_path: Path,
) -> None:
    summary = AnswerEvaluationSummary(
        total=1,
        passed=1,
        failed=0,
        results=[
            AnswerEvaluationResult(
                question="What should happen if a QR payment failed?",
                expected_answer_type="direct_answer",
                expected_behavior="Explain the dispute process.",
                answer=(
                    "Customers may raise a dispute.\n\n"
                    "Source: [Source 1] digital_payments.md, QR Payment Disputes."
                ),
                has_sources=True,
                forbidden_terms_found=[],
                no_answer_language_detected=False,
                cited_source_numbers=[1],
                invalid_source_numbers=[],
                citation_validation_passed=True,
                passed=True,
            )
        ],
    )

    writer = AnswerEvaluationReportWriter(reports_dir=tmp_path)

    json_path, markdown_path = writer.write(
        summary=summary,
        report_name="test_answer_eval",
    )

    assert json_path.exists()
    assert markdown_path.exists()

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert json_payload["evaluation_type"] == "answer_evaluation"
    assert json_payload["summary"]["total"] == 1
    assert json_payload["summary"]["passed"] == 1
    assert json_payload["summary"]["failed"] == 0
    assert json_payload["summary"]["results"][0]["cited_source_numbers"] == [1]

    markdown_text = markdown_path.read_text(encoding="utf-8")

    assert "# Answer Evaluation Report" in markdown_text
    assert "Passed: 1" in markdown_text
    assert "Question 1: PASS" in markdown_text
    assert "Citation validation passed: True" in markdown_text
    assert "Customers may raise a dispute." in markdown_text
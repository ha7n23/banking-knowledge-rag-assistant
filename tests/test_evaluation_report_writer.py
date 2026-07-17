import json
from pathlib import Path

from banking_rag.core.schemas import (
    AnswerEvaluationResult,
    AnswerEvaluationSummary,
)
from banking_rag.services.evaluation_report_writer import (
    AnswerEvaluationReportWriter,
)


def build_sample_summary() -> AnswerEvaluationSummary:
    """Build a small answer evaluation summary for report tests."""
    return AnswerEvaluationSummary(
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


def test_answer_evaluation_report_writer_creates_latest_reports(
    tmp_path: Path,
) -> None:
    summary = build_sample_summary()

    writer = AnswerEvaluationReportWriter(reports_dir=tmp_path)

    (
        latest_json_path,
        latest_markdown_path,
        timestamped_json_path,
        timestamped_markdown_path,
    ) = writer.write(
        summary=summary,
        report_name="test_answer_eval_latest",
        write_timestamped=False,
    )

    assert latest_json_path.exists()
    assert latest_markdown_path.exists()
    assert timestamped_json_path is None
    assert timestamped_markdown_path is None

    json_payload = json.loads(latest_json_path.read_text(encoding="utf-8"))

    assert json_payload["evaluation_type"] == "answer_evaluation"
    assert json_payload["summary"]["total"] == 1
    assert json_payload["summary"]["passed"] == 1
    assert json_payload["summary"]["failed"] == 0
    assert json_payload["summary"]["results"][0]["cited_source_numbers"] == [1]

    markdown_text = latest_markdown_path.read_text(encoding="utf-8")

    assert "# Answer Evaluation Report" in markdown_text
    assert "Passed: 1" in markdown_text
    assert "Question 1: PASS" in markdown_text
    assert "Citation validation passed: True" in markdown_text
    assert "Customers may raise a dispute." in markdown_text


def test_answer_evaluation_report_writer_creates_timestamped_reports(
    tmp_path: Path,
) -> None:
    summary = build_sample_summary()

    writer = AnswerEvaluationReportWriter(reports_dir=tmp_path)

    (
        latest_json_path,
        latest_markdown_path,
        timestamped_json_path,
        timestamped_markdown_path,
    ) = writer.write(
        summary=summary,
        report_name="answer_eval_latest",
        write_timestamped=True,
    )

    assert latest_json_path.exists()
    assert latest_markdown_path.exists()
    assert timestamped_json_path is not None
    assert timestamped_markdown_path is not None
    assert timestamped_json_path.exists()
    assert timestamped_markdown_path.exists()

    assert latest_json_path.name == "answer_eval_latest.json"
    assert latest_markdown_path.name == "answer_eval_latest.md"

    assert timestamped_json_path.name.startswith("answer_eval_")
    assert timestamped_json_path.name.endswith(".json")
    assert timestamped_markdown_path.name.startswith("answer_eval_")
    assert timestamped_markdown_path.name.endswith(".md")
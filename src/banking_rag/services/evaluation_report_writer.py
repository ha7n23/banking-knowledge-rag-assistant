import json
from datetime import datetime, timezone
from pathlib import Path

from banking_rag.core.config import EVALUATION_REPORTS_DIR
from banking_rag.core.schemas import AnswerEvaluationSummary


class AnswerEvaluationReportWriter:
    """Writes answer evaluation results to JSON and Markdown reports."""

    def __init__(
        self,
        reports_dir: Path = EVALUATION_REPORTS_DIR,
    ) -> None:
        self.reports_dir = reports_dir

    def write(
        self,
        summary: AnswerEvaluationSummary,
        report_name: str = "answer_eval_latest",
    ) -> tuple[Path, Path]:
        """Write JSON and Markdown reports for an answer evaluation summary."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / f"{report_name}.json"
        markdown_path = self.reports_dir / f"{report_name}.md"

        generated_at_utc = datetime.now(timezone.utc).isoformat()

        self._write_json_report(
            summary=summary,
            json_path=json_path,
            generated_at_utc=generated_at_utc,
        )
        self._write_markdown_report(
            summary=summary,
            markdown_path=markdown_path,
            generated_at_utc=generated_at_utc,
        )

        return json_path, markdown_path

    def _write_json_report(
        self,
        summary: AnswerEvaluationSummary,
        json_path: Path,
        generated_at_utc: str,
    ) -> None:
        """Write a machine-readable JSON evaluation report."""
        payload = {
            "generated_at_utc": generated_at_utc,
            "evaluation_type": "answer_evaluation",
            "summary": summary.model_dump(),
        }

        json_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def _write_markdown_report(
        self,
        summary: AnswerEvaluationSummary,
        markdown_path: Path,
        generated_at_utc: str,
    ) -> None:
        """Write a human-readable Markdown evaluation report."""
        lines: list[str] = [
            "# Answer Evaluation Report",
            "",
            f"Generated at UTC: `{generated_at_utc}`",
            "",
            "## Summary",
            "",
            f"- Passed: {summary.passed}",
            f"- Failed: {summary.failed}",
            f"- Total: {summary.total}",
            "",
            "## Results",
            "",
        ]

        for index, result in enumerate(summary.results, start=1):
            status = "PASS" if result.passed else "FAIL"

            lines.extend(
                [
                    f"### Question {index}: {status}",
                    "",
                    f"**Question:** {result.question}",
                    "",
                    f"**Expected answer type:** `{result.expected_answer_type}`",
                    "",
                    f"**Expected behavior:** {result.expected_behavior}",
                    "",
                    f"- Has sources: {result.has_sources}",
                    (
                        "- Citation validation passed: "
                        f"{result.citation_validation_passed}"
                    ),
                    f"- Cited source numbers: {result.cited_source_numbers}",
                    f"- Invalid source numbers: {result.invalid_source_numbers}",
                    (
                        "- No-answer language detected: "
                        f"{result.no_answer_language_detected}"
                    ),
                    f"- Forbidden terms found: {result.forbidden_terms_found}",
                    "",
                    "**Answer:**",
                    "",
                    result.answer,
                    "",
                ]
            )

        markdown_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )
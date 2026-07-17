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
        write_timestamped: bool = True,
    ) -> tuple[Path, Path, Path | None, Path | None]:
        """
        Write latest and optional timestamped evaluation reports.

        Returns:
            latest_json_path, latest_markdown_path,
            timestamped_json_path, timestamped_markdown_path
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        generated_at = datetime.now(timezone.utc)
        generated_at_utc = generated_at.isoformat()

        latest_json_path = self.reports_dir / f"{report_name}.json"
        latest_markdown_path = self.reports_dir / f"{report_name}.md"

        self._write_json_report(
            summary=summary,
            json_path=latest_json_path,
            generated_at_utc=generated_at_utc,
        )
        self._write_markdown_report(
            summary=summary,
            markdown_path=latest_markdown_path,
            generated_at_utc=generated_at_utc,
        )

        timestamped_json_path: Path | None = None
        timestamped_markdown_path: Path | None = None

        if write_timestamped:
            timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
            timestamped_report_name = self._build_timestamped_report_name(
                report_name=report_name,
                timestamp=timestamp,
            )

            timestamped_json_path = (
                self.reports_dir / f"{timestamped_report_name}.json"
            )
            timestamped_markdown_path = (
                self.reports_dir / f"{timestamped_report_name}.md"
            )

            self._write_json_report(
                summary=summary,
                json_path=timestamped_json_path,
                generated_at_utc=generated_at_utc,
            )
            self._write_markdown_report(
                summary=summary,
                markdown_path=timestamped_markdown_path,
                generated_at_utc=generated_at_utc,
            )

        return (
            latest_json_path,
            latest_markdown_path,
            timestamped_json_path,
            timestamped_markdown_path,
        )

    def _build_timestamped_report_name(
        self,
        report_name: str,
        timestamp: str,
    ) -> str:
        """Build a timestamped report name from a base report name."""
        base_name = report_name.removesuffix("_latest")

        return f"{base_name}_{timestamp}"

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
import re

from banking_rag.core.schemas import CitationValidationResult


SOURCE_CITATION_PATTERN = re.compile(
    r"\[(?:Source\s+)?(\d+)\]",
    flags=re.IGNORECASE,
)


class CitationValidationService:
    """Validates whether generated answer citations refer to retrieved sources."""

    def validate(
        self,
        answer: str,
        source_count: int,
    ) -> CitationValidationResult:
        """Validate source-number citations in a generated answer."""
        cited_source_numbers = self._extract_cited_source_numbers(answer)

        invalid_source_numbers = [
            source_number
            for source_number in cited_source_numbers
            if source_number < 1 or source_number > source_count
        ]

        has_at_least_one_citation = len(cited_source_numbers) > 0

        passed = (
            has_at_least_one_citation
            and len(invalid_source_numbers) == 0
        )

        return CitationValidationResult(
            cited_source_numbers=cited_source_numbers,
            invalid_source_numbers=invalid_source_numbers,
            source_count=source_count,
            has_at_least_one_citation=has_at_least_one_citation,
            passed=passed,
        )

    def _extract_cited_source_numbers(self, answer: str) -> list[int]:
        """Extract unique cited source numbers from answer text."""
        matches = SOURCE_CITATION_PATTERN.findall(answer)

        source_numbers = [int(match) for match in matches]

        return sorted(set(source_numbers))
from banking_rag.services.citation_validation_service import (
    CitationValidationService,
)


def test_citation_validation_passes_valid_citations() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer=(
            "Customers may raise a dispute.\n\n"
            "Source: [Source 1] digital_payments.md, QR Payment Disputes."
        ),
        source_count=3,
    )

    assert result.cited_source_numbers == [1]
    assert result.invalid_source_numbers == []
    assert result.source_count == 3
    assert result.has_at_least_one_citation is True
    assert result.passed is True


def test_citation_validation_fails_invalid_source_number() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer=(
            "Customers may raise a dispute.\n\n"
            "Source: [Source 5] digital_payments.md, QR Payment Disputes."
        ),
        source_count=3,
    )

    assert result.cited_source_numbers == [5]
    assert result.invalid_source_numbers == [5]
    assert result.passed is False


def test_citation_validation_fails_missing_citation() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer="Customers may raise a dispute.",
        source_count=3,
    )

    assert result.cited_source_numbers == []
    assert result.invalid_source_numbers == []
    assert result.has_at_least_one_citation is False
    assert result.passed is False


def test_citation_validation_handles_multiple_citations() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer=(
            "QR disputes may be raised. [Source 1]\n"
            "Password recovery is handled in the app. [Source 2]"
        ),
        source_count=2,
    )

    assert result.cited_source_numbers == [1, 2]
    assert result.invalid_source_numbers == []
    assert result.passed is True


def test_citation_validation_deduplicates_repeated_citations() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer="Disputes may be raised. [Source 1] [Source 1]",
        source_count=2,
    )

    assert result.cited_source_numbers == [1]
    assert result.invalid_source_numbers == []
    assert result.passed is True


def test_citation_validation_is_case_insensitive() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer="Disputes may be raised. [source 1]",
        source_count=1,
    )

    assert result.cited_source_numbers == [1]
    assert result.passed is True

def test_citation_validation_accepts_numeric_bracket_citations() -> None:
    service = CitationValidationService()

    result = service.validate(
        answer=(
            "Customers should use the forgot password option.\n\n"
            "Source: [1] mobile_app_access.md, Password Recovery."
        ),
        source_count=1,
    )

    assert result.cited_source_numbers == [1]
    assert result.invalid_source_numbers == []
    assert result.passed is True
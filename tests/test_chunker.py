import pytest

from banking_rag.core.exceptions import ChunkingError
from banking_rag.core.schemas import RawDocument
from banking_rag.ingestion.chunker import (
    chunk_documents,
    extract_markdown_sections,
    split_long_text_with_overlap,
)


def test_extract_markdown_sections_splits_by_level_two_headings() -> None:
    text = """
# Banking Policy

## QR Payments

QR payment dispute content.

## Password Recovery

Password recovery content.
""".strip()

    sections = extract_markdown_sections(text)

    assert len(sections) == 2
    assert sections[0][0] == "QR Payments"
    assert "QR payment dispute content." in sections[0][1]
    assert sections[1][0] == "Password Recovery"
    assert "Password recovery content." in sections[1][1]


def test_chunk_documents_creates_source_traceable_chunks() -> None:
    document = RawDocument(
        source="digital_payments.md",
        text="""
# Digital Payments

## QR Payment Disputes

Customers may raise a dispute if a QR payment is deducted but the merchant does not receive funds.

## Payment Safety

Customers should verify merchant details before confirming payment.
""".strip(),
        metadata={"file_type": "markdown"},
    )

    chunks = chunk_documents(
        documents=[document],
        chunk_size=900,
        chunk_overlap=120,
    )

    assert len(chunks) == 2

    assert chunks[0].source == "digital_payments.md"
    assert chunks[0].section == "QR Payment Disputes"
    assert "QR payment is deducted" in chunks[0].text

    assert chunks[1].section == "Payment Safety"
    assert chunks[1].metadata["section"] == "Payment Safety"


def test_extract_markdown_sections_handles_document_without_headings() -> None:
    text = "This document has no markdown headings."

    sections = extract_markdown_sections(text)

    assert len(sections) == 1
    assert sections[0][0] == "Document"
    assert sections[0][1] == text


def test_split_long_text_with_overlap_rejects_invalid_settings() -> None:
    with pytest.raises(ChunkingError):
        split_long_text_with_overlap(
            text="example",
            chunk_size=100,
            chunk_overlap=100,
        )
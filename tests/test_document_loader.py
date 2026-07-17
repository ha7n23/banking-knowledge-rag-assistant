from pathlib import Path

import pytest

from banking_rag.core.exceptions import DocumentLoadingError
from banking_rag.ingestion import document_loader
from banking_rag.ingestion.document_loader import (
    clean_extracted_pdf_text,
    load_documents,
    load_markdown_documents,
    load_pdf_documents,
)


def test_load_markdown_documents_loads_only_markdown_files(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    markdown_file = docs_dir / "policy.md"
    markdown_file.write_text("# Policy\n\n## Section\n\nSome content.", encoding="utf-8")

    text_file = docs_dir / "notes.txt"
    text_file.write_text("This should not be loaded.", encoding="utf-8")

    documents = load_markdown_documents(docs_dir)

    assert len(documents) == 1
    assert documents[0].source == "policy.md"
    assert "Some content" in documents[0].text
    assert documents[0].metadata["file_type"] == "markdown"


def test_load_markdown_documents_ignores_empty_markdown_files(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    empty_file = docs_dir / "empty.md"
    empty_file.write_text("", encoding="utf-8")

    documents = load_markdown_documents(docs_dir)

    assert documents == []


def test_load_markdown_documents_raises_for_missing_directory(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"

    with pytest.raises(DocumentLoadingError):
        load_markdown_documents(missing_dir)

def test_load_markdown_documents_adds_inferred_metadata(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "digital_payments.md").write_text(
        "# Digital Payments\n\n## QR Payment Disputes\n\nSome content.",
        encoding="utf-8",
    )

    documents = load_markdown_documents(docs_dir)

    assert len(documents) == 1
    assert documents[0].metadata["file_name"] == "digital_payments.md"
    assert documents[0].metadata["file_type"] == "markdown"
    assert documents[0].metadata["document_type"] == "policy"
    assert documents[0].metadata["product"] == "digital_payments"
    assert documents[0].metadata["channel"] == "qr"

class FakePdfPage:
    """Fake PDF page for testing PDF extraction."""

    def __init__(self, text: str) -> None:
        self.text = text

    def extract_text(self) -> str:
        return self.text


class FakePdfReader:
    """Fake PdfReader for testing without creating real PDF files."""

    def __init__(self, file_path: Path) -> None:
        self.pages = [
            FakePdfPage("QR payment dispute text.\n\nMerchant did not receive."),
            FakePdfPage("Second page text about settlement records."),
        ]


def test_clean_extracted_pdf_text_removes_blank_lines() -> None:
    text = "Line one\n\n\nLine two   with   spaces\n"

    cleaned = clean_extracted_pdf_text(text)

    assert cleaned == "Line one\nLine two with spaces"


def test_load_pdf_documents_converts_pages_to_markdown_sections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "digital_payments_policy.pdf").write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(document_loader, "PdfReader", FakePdfReader)

    documents = load_pdf_documents(docs_dir)

    assert len(documents) == 1
    assert documents[0].source == "digital_payments_policy.pdf"
    assert documents[0].metadata["file_name"] == "digital_payments_policy.pdf"
    assert documents[0].metadata["file_type"] == "pdf"
    assert documents[0].metadata["page_count"] == 2
    assert documents[0].metadata["product"] == "digital_payments"
    assert "# digital_payments_policy.pdf" in documents[0].text
    assert "## Page 1" in documents[0].text
    assert "QR payment dispute text." in documents[0].text
    assert "## Page 2" in documents[0].text
    assert "Second page text about settlement records." in documents[0].text


def test_load_documents_loads_markdown_and_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "mobile_app_access.md").write_text(
        "# Mobile App\n\n## Password Recovery\n\nUse forgot password.",
        encoding="utf-8",
    )
    (docs_dir / "digital_payments_policy.pdf").write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(document_loader, "PdfReader", FakePdfReader)

    documents = load_documents(docs_dir)

    assert len(documents) == 2
    assert {document.metadata["file_type"] for document in documents} == {
        "markdown",
        "pdf",
    }
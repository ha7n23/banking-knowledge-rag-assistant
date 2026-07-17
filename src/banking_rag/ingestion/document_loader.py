from pathlib import Path

from pypdf import PdfReader

from banking_rag.core.exceptions import DocumentLoadingError
from banking_rag.core.schemas import MetadataValue, RawDocument


def load_documents(docs_dir: Path) -> list[RawDocument]:
    """Load all supported document types from a directory."""
    return [
        *load_markdown_documents(docs_dir),
        *load_pdf_documents(docs_dir),
    ]


def load_markdown_documents(docs_dir: Path) -> list[RawDocument]:
    """
    Load markdown documents from a directory.

    Only .md files are loaded. Each document keeps its source filename
    and simple metadata so later chunks can be cited back to the source.
    """
    _validate_docs_dir(docs_dir)

    documents: list[RawDocument] = []

    for file_path in sorted(docs_dir.glob("*.md")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(
            RawDocument(
                source=file_path.name,
                text=text,
                metadata={
                    "file_name": file_path.name,
                    "file_type": "markdown",
                    **infer_document_metadata(file_path.name),
                },
            )
        )

    return documents


def load_pdf_documents(docs_dir: Path) -> list[RawDocument]:
    """
    Load PDF documents from a directory.

    Each PDF is converted into markdown-like text where every page becomes
    a section. This allows the existing heading-aware chunker to process PDFs.
    """
    _validate_docs_dir(docs_dir)

    documents: list[RawDocument] = []

    for file_path in sorted(docs_dir.glob("*.pdf")):
        text, page_count = extract_pdf_text_as_markdown(file_path)

        if not text.strip():
            continue

        documents.append(
            RawDocument(
                source=file_path.name,
                text=text,
                metadata={
                    "file_name": file_path.name,
                    "file_type": "pdf",
                    "page_count": page_count,
                    **infer_document_metadata(file_path.name),
                },
            )
        )

    return documents


def extract_pdf_text_as_markdown(file_path: Path) -> tuple[str, int]:
    """Extract PDF text and convert pages into markdown-like sections."""
    try:
        reader = PdfReader(file_path)
    except Exception as error:
        raise DocumentLoadingError(
            f"Failed to open PDF document: {file_path}"
        ) from error

    markdown_parts: list[str] = [f"# {file_path.name}"]
    extracted_page_count = 0

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""

        cleaned_page_text = clean_extracted_pdf_text(page_text)

        if not cleaned_page_text:
            continue

        markdown_parts.append(f"## Page {page_number}")
        markdown_parts.append(cleaned_page_text)
        extracted_page_count += 1

    return "\n\n".join(markdown_parts).strip(), extracted_page_count


def clean_extracted_pdf_text(text: str) -> str:
    """Clean common PDF text extraction artifacts."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    cleaned_text = "\n".join(lines)

    while "  " in cleaned_text:
        cleaned_text = cleaned_text.replace("  ", " ")

    return cleaned_text.strip()


def infer_document_metadata(file_name: str) -> dict[str, MetadataValue]:
    """Infer simple metadata fields from known sample document names."""
    normalized_name = file_name.lower()
    stem = Path(file_name).stem.lower()

    if file_name == "digital_payments.md" or "digital_payment" in stem:
        return {
            "document_type": "policy",
            "product": "digital_payments",
            "channel": "qr",
            "authority": "internal_mock_policy",
        }

    if (
        file_name == "mobile_app_access.md"
        or "mobile_app" in stem
        or "app_access" in stem
    ):
        return {
            "document_type": "policy",
            "product": "mobile_app",
            "channel": "mobile_app",
            "authority": "internal_mock_policy",
        }

    if file_name == "card_disputes.md" or "card" in normalized_name:
        return {
            "document_type": "policy",
            "product": "cards",
            "channel": "card",
            "authority": "internal_mock_policy",
        }

    return {
        "document_type": "unknown",
        "product": "unknown",
        "channel": "unknown",
        "authority": "unknown",
    }


def _validate_docs_dir(docs_dir: Path) -> None:
    """Validate that the document directory exists and is a directory."""
    if not docs_dir.exists():
        raise DocumentLoadingError(f"Document directory does not exist: {docs_dir}")

    if not docs_dir.is_dir():
        raise DocumentLoadingError(f"Document path is not a directory: {docs_dir}")
from pathlib import Path

from banking_rag.core.exceptions import DocumentLoadingError
from banking_rag.core.schemas import RawDocument

from banking_rag.core.schemas import MetadataValue


def load_markdown_documents(docs_dir: Path) -> list[RawDocument]:
    """
    Load markdown documents from a directory.

    Only .md files are loaded. Each document keeps its source filename
    and simple metadata so later chunks can be cited back to the source.
    """
    if not docs_dir.exists():
        raise DocumentLoadingError(f"Document directory does not exist: {docs_dir}")

    if not docs_dir.is_dir():
        raise DocumentLoadingError(f"Document path is not a directory: {docs_dir}")

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

def infer_document_metadata(file_name: str) -> dict[str, MetadataValue]:
    """Infer simple metadata fields from known sample document names."""
    if file_name == "digital_payments.md":
        return {
            "document_type": "policy",
            "product": "digital_payments",
            "channel": "qr",
            "authority": "internal_mock_policy",
        }

    if file_name == "mobile_app_access.md":
        return {
            "document_type": "policy",
            "product": "mobile_app",
            "channel": "mobile_app",
            "authority": "internal_mock_policy",
        }

    if file_name == "card_disputes.md":
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
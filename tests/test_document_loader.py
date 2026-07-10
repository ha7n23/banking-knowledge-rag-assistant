from pathlib import Path

import pytest

from banking_rag.core.exceptions import DocumentLoadingError
from banking_rag.ingestion.document_loader import load_markdown_documents


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
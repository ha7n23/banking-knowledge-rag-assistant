from banking_rag.core.exceptions import ChunkingError
from banking_rag.core.schemas import DocumentChunk, RawDocument


def extract_markdown_sections(text: str) -> list[tuple[str, str]]:
    """
    Split a markdown document into sections using ## headings.

    Each section keeps the document title and section heading so the chunk
    remains understandable when retrieved on its own.
    """
    lines = text.splitlines()

    document_title = ""
    current_heading: str | None = None
    current_lines: list[str] = []
    sections: list[tuple[str, str]] = []

    def flush_current_section() -> None:
        if current_heading is None:
            return

        body = "\n".join(current_lines).strip()

        if not body:
            return

        section_name = current_heading.lstrip("#").strip()

        parts: list[str] = []

        if document_title:
            parts.append(document_title)

        parts.append(current_heading)
        parts.append(body)

        section_text = "\n\n".join(parts)
        sections.append((section_name, section_text))

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# "):
            document_title = stripped

        elif stripped.startswith("## "):
            flush_current_section()
            current_heading = stripped
            current_lines = []

        else:
            if current_heading is not None:
                current_lines.append(line)

    flush_current_section()

    if not sections and text.strip():
        sections.append(("Document", text.strip()))

    return sections


def split_long_text_with_overlap(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Split long text into overlapping chunks.

    This is a fallback for sections that are too long. For normal short
    markdown sections, the whole section stays as one clean chunk.
    """
    if chunk_size <= 0:
        raise ChunkingError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise ChunkingError("chunk_overlap cannot be negative.")

    if chunk_size <= chunk_overlap:
        raise ChunkingError("chunk_size must be greater than chunk_overlap.")

    cleaned_text = text.strip()

    if not cleaned_text:
        return []

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks: list[str] = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def chunk_documents(
    documents: list[RawDocument],
    chunk_size: int,
    chunk_overlap: int,
) -> list[DocumentChunk]:
    """Convert raw documents into clean, source-traceable chunks."""
    chunks: list[DocumentChunk] = []

    for document in documents:
        sections = extract_markdown_sections(document.text)
        document_chunk_index = 0

        for section_name, section_text in sections:
            section_chunks = split_long_text_with_overlap(
                text=section_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            for section_chunk in section_chunks:
                chunk_id = f"{document.source}::chunk_{document_chunk_index}"

                chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        text=section_chunk,
                        source=document.source,
                        section=section_name,
                        chunk_index=document_chunk_index,
                        metadata={
                            **document.metadata,
                            "section": section_name,
                            "chunk_index": document_chunk_index,
                        },
                    )
                )

                document_chunk_index += 1

    return chunks
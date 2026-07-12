from pydantic import BaseModel, Field


MetadataValue = str | int | float | bool


class RawDocument(BaseModel):
    """A raw document loaded from disk before chunking."""

    source: str
    text: str
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """A clean searchable chunk created from a raw document."""

    id: str
    text: str
    source: str
    section: str
    chunk_index: int
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)

class RetrievedChunk(BaseModel):
    """A chunk returned by the retriever for a user query."""

    text: str
    source: str
    section: str
    chunk_index: int
    distance: float
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)

class SourceReference(BaseModel):
    """A source used to support a generated answer."""

    source: str
    section: str
    chunk_index: int
    distance: float


class RAGAnswer(BaseModel):
    """Final grounded answer returned by the RAG service."""

    question: str
    answer: str
    sources: list[SourceReference]
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
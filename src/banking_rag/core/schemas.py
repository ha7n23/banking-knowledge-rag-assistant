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
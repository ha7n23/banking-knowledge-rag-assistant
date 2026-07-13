from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Basic API health response."""

    status: str
    app_name: str
    environment: str


class RetrievedChunkAPIResponse(BaseModel):
    """Retrieved chunk returned through the API."""

    text: str
    source: str
    section: str
    chunk_index: int
    distance: float


class RetrieveRequest(BaseModel):
    """Request body for retrieval-only endpoint."""

    query: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=10)


class RetrieveResponse(BaseModel):
    """Response body for retrieval-only endpoint."""

    query: str
    chunks: list[RetrievedChunkAPIResponse]


class SourceReferenceAPIResponse(BaseModel):
    """Source reference returned with an answer."""

    source: str
    section: str
    chunk_index: int
    distance: float


class AnswerRequest(BaseModel):
    """Request body for full RAG answer endpoint."""

    query: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=10)


class AnswerResponse(BaseModel):
    """Response body for full RAG answer endpoint."""

    question: str
    answer: str
    sources: list[SourceReferenceAPIResponse]
    retrieved_chunks: list[RetrievedChunkAPIResponse]
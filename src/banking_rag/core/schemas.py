from typing import Literal
from pydantic import BaseModel, Field


MetadataValue = str | int | float | bool

ExpectedAnswerType = Literal["direct_answer", "no_answer"]

RetrievalMode = Literal["semantic", "hybrid"]


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

class HybridRetrievedChunk(RetrievedChunk):
    """Retrieved chunk with hybrid retrieval scoring information."""

    semantic_rank: int | None = None
    keyword_score: float = 0.0
    hybrid_score: float = 0.0

class RerankedChunk(HybridRetrievedChunk):
    """Retrieved chunk with reranking information."""

    original_rank: int
    rerank_keyword_score: float = 0.0
    rerank_section_score: float = 0.0
    rerank_score: float = 0.0


class SourceReference(BaseModel):
    """A source used to support a generated answer."""

    source: str
    section: str
    chunk_index: int
    distance: float

class QueryRewriteResult(BaseModel):
    """Result of conservative query rewriting."""

    original_query: str
    rewritten_query: str
    was_rewritten: bool
    reason: str


class RAGAnswer(BaseModel):
    """Final grounded answer returned by the RAG service."""

    question: str
    answer: str
    sources: list[SourceReference]
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    retrieval_query: str | None = None
    metadata_filter: dict[str, MetadataValue] | None = None
    retrieval_mode: RetrievalMode = "semantic"
    rerank_enabled: bool = False
    query_was_rewritten: bool = False
    rewrite_reason: str | None = None

class EvaluationQuestion(BaseModel):
    """A question used to evaluate retrieval quality."""

    question: str
    expected_top_source: str
    expected_top_section: str
    expected_behavior: str
    expected_answer_type: ExpectedAnswerType = "direct_answer"
    must_not_include: list[str] = Field(default_factory=list)


class RetrievalEvaluationResult(BaseModel):
    """Result of evaluating one retrieval question."""

    question: str
    expected_top_source: str
    expected_top_section: str
    retrieved_top_source: str
    retrieved_top_section: str
    retrieved_distance: float
    expected_behavior: str
    expected_answer_type: ExpectedAnswerType
    must_not_include: list[str]
    expected_rank: int | None
    top_1_passed: bool
    top_k_passed: bool
    passed: bool


class EvaluationSummary(BaseModel):
    """Summary of retrieval evaluation results."""

    total: int
    top_1_passed: int
    top_k_passed: int
    failed_top_k: int
    results: list[RetrievalEvaluationResult]

RetrievedResultChunk = RerankedChunk | HybridRetrievedChunk | RetrievedChunk

class RetrievalPipelineResult(BaseModel):
    """Result from the reusable retrieval pipeline."""

    original_query: str
    retrieval_query: str
    rewrite_result: QueryRewriteResult | None = None
    metadata_filter: dict[str, MetadataValue] | None = None
    retrieval_mode: RetrievalMode
    rerank_enabled: bool
    retrieved_chunks: list[RetrievedResultChunk]

class AnswerEvaluationResult(BaseModel):
    """Result of evaluating one generated RAG answer."""

    question: str
    expected_answer_type: ExpectedAnswerType
    expected_behavior: str
    answer: str
    has_sources: bool
    forbidden_terms_found: list[str]
    no_answer_language_detected: bool
    passed: bool


class AnswerEvaluationSummary(BaseModel):
    """Summary of generated answer evaluation results."""

    total: int
    passed: int
    failed: int
    results: list[AnswerEvaluationResult]
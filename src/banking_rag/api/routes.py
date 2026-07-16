from fastapi import APIRouter, Depends, HTTPException, status

from banking_rag.api.dependencies import get_rag_service, get_retriever
from banking_rag.api.schemas import (
    AnswerRequest,
    AnswerResponse,
    HealthResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrievedChunkAPIResponse,
    SourceReferenceAPIResponse,
)
from banking_rag.core.config import APP_NAME, ENVIRONMENT
from banking_rag.core.exceptions import GenerationError, RetrievalError
from banking_rag.core.schemas import RAGAnswer, RetrievedChunk
from banking_rag.retrieval.retriever import KnowledgeRetriever
from banking_rag.services.rag_service import BankingRAGService


router = APIRouter()


def to_retrieved_chunk_response(
    chunk: RetrievedChunk,
) -> RetrievedChunkAPIResponse:
    """Convert an internal RetrievedChunk into an API response model."""
    return RetrievedChunkAPIResponse(
        text=chunk.text,
        source=chunk.source,
        section=chunk.section,
        chunk_index=chunk.chunk_index,
        distance=chunk.distance,
    )


def to_answer_response(result: RAGAnswer) -> AnswerResponse:
    """Convert an internal RAGAnswer into an API response model."""
    return AnswerResponse(
        question=result.question,
        answer=result.answer,
        sources=[
            SourceReferenceAPIResponse(
                source=source.source,
                section=source.section,
                chunk_index=source.chunk_index,
                distance=source.distance,
            )
            for source in result.sources
        ],
        retrieved_chunks=[
            to_retrieved_chunk_response(chunk)
            for chunk in result.retrieved_chunks
        ],
        retrieval_query=result.retrieval_query,
        metadata_filter=result.metadata_filter,
        retrieval_mode=result.retrieval_mode,
        rerank_enabled=result.rerank_enabled,
        query_was_rewritten=result.query_was_rewritten,
        rewrite_reason=result.rewrite_reason,
    )


@router.get("/")
def root() -> dict[str, str]:
    """Return a simple API root message."""
    return {
        "message": "Banking Knowledge RAG Assistant API",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return basic API health status."""
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        environment=ENVIRONMENT,
    )


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_chunks(
    request: RetrieveRequest,
    retriever: KnowledgeRetriever = Depends(get_retriever),
) -> RetrieveResponse:
    """Retrieve relevant chunks for a user query."""
    try:
        chunks = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
        )
    except RetrievalError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return RetrieveResponse(
        query=request.query,
        chunks=[
            to_retrieved_chunk_response(chunk)
            for chunk in chunks
        ],
    )


@router.post("/answer", response_model=AnswerResponse)
def answer_question(
    request: AnswerRequest,
    rag_service: BankingRAGService = Depends(get_rag_service),
) -> AnswerResponse:
    """Generate a grounded RAG answer for a user query."""
    try:
        result = rag_service.answer(
            question=request.query,
            top_k=request.top_k,
            retrieval_mode=request.retrieval_mode,
            auto_filter=request.auto_filter,
            rewrite_query=request.rewrite_query,
            rerank=request.rerank,
            candidate_k=request.candidate_k,
        )
    except RetrievalError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except GenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return to_answer_response(result)
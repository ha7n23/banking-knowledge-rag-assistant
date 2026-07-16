from typing import Protocol

from banking_rag.core.schemas import (
    MetadataValue,
    RAGAnswer,
    RetrievalMode,
    RetrievalPipelineResult,
    RetrievedChunk,
    SourceReference,
)
from banking_rag.generation.llm_client import GeminiLLMClient, TextGenerator
from banking_rag.generation.prompt_builder import build_grounded_prompt
from banking_rag.retrieval.retrieval_pipeline import RetrievalPipeline


class RetrievalPipelineProtocol(Protocol):
    """Protocol for any retrieval pipeline used by the RAG service."""

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        retrieval_mode: RetrievalMode = "semantic",
        metadata_filter: dict[str, MetadataValue] | None = None,
        auto_filter: bool = False,
        rewrite_query_enabled: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> RetrievalPipelineResult:
        """Run retrieval and return pipeline metadata plus retrieved chunks."""
        ...


class BankingRAGService:
    """Combines advanced retrieval and generation into a grounded RAG workflow."""

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipelineProtocol | None = None,
        llm_client: TextGenerator | None = None,
    ) -> None:
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline()
        self.llm_client = llm_client or GeminiLLMClient()

    def answer(
        self,
        question: str,
        top_k: int | None = None,
        retrieval_mode: RetrievalMode = "semantic",
        metadata_filter: dict[str, MetadataValue] | None = None,
        auto_filter: bool = False,
        rewrite_query: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> RAGAnswer:
        """Retrieve context with the advanced pipeline and generate a grounded answer."""
        pipeline_result = self.retrieval_pipeline.retrieve(
            query=question,
            top_k=top_k,
            retrieval_mode=retrieval_mode,
            metadata_filter=metadata_filter,
            auto_filter=auto_filter,
            rewrite_query_enabled=rewrite_query,
            rerank=rerank,
            candidate_k=candidate_k,
        )

        retrieved_chunks_for_prompt: list[RetrievedChunk] = []

        for chunk in pipeline_result.retrieved_chunks:
            retrieved_chunks_for_prompt.append(chunk)

        prompt = build_grounded_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks_for_prompt,
        )

        answer_text = self.llm_client.generate(prompt)

        sources = [
            SourceReference(
                source=chunk.source,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                distance=chunk.distance,
            )
            for chunk in pipeline_result.retrieved_chunks
        ]

        query_was_rewritten = False
        rewrite_reason = None

        if pipeline_result.rewrite_result is not None:
            query_was_rewritten = pipeline_result.rewrite_result.was_rewritten
            rewrite_reason = pipeline_result.rewrite_result.reason

        return RAGAnswer(
            question=question,
            answer=answer_text,
            sources=sources,
            retrieved_chunks=pipeline_result.retrieved_chunks,
            retrieval_query=pipeline_result.retrieval_query,
            metadata_filter=pipeline_result.metadata_filter,
            retrieval_mode=pipeline_result.retrieval_mode,
            rerank_enabled=pipeline_result.rerank_enabled,
            query_was_rewritten=query_was_rewritten,
            rewrite_reason=rewrite_reason,
        )
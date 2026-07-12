from typing import Protocol

from banking_rag.core.schemas import RAGAnswer, RetrievedChunk, SourceReference
from banking_rag.generation.llm_client import GeminiLLMClient, TextGenerator
from banking_rag.generation.prompt_builder import build_grounded_prompt
from banking_rag.retrieval.retriever import KnowledgeRetriever


class RetrieverProtocol(Protocol):
    """Protocol for any retriever used by the RAG service."""

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Retrieve relevant chunks for a query."""
        ...


class BankingRAGService:
    """Combines retrieval and generation into a grounded RAG workflow."""

    def __init__(
        self,
        retriever: RetrieverProtocol | None = None,
        llm_client: TextGenerator | None = None,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.llm_client = llm_client or GeminiLLMClient()

    def answer(self, question: str, top_k: int | None = None) -> RAGAnswer:
        """Retrieve context and generate a grounded answer."""
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        prompt = build_grounded_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        answer_text = self.llm_client.generate(prompt)

        sources = [
            SourceReference(
                source=chunk.source,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                distance=chunk.distance,
            )
            for chunk in retrieved_chunks
        ]

        return RAGAnswer(
            question=question,
            answer=answer_text,
            sources=sources,
            retrieved_chunks=retrieved_chunks,
        )
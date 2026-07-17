from banking_rag.core.schemas import (
    MetadataValue,
    QueryRewriteResult,
    RAGAnswer,
    RetrievalMode,
    RetrievalPipelineResult,
    RetrievedChunk,
)
from banking_rag.services.rag_service import BankingRAGService


class FakeRetrievalPipeline:
    """Fake retrieval pipeline for testing the RAG service."""

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
        retrieval_query = query

        rewrite_result = None

        if rewrite_query_enabled:
            retrieval_query = (
                "QR payment deducted from customer account but merchant "
                "did not receive payment confirmation"
            )
            rewrite_result = QueryRewriteResult(
                original_query=query,
                rewritten_query=retrieval_query,
                was_rewritten=True,
                reason="Detected likely QR payment deducted but merchant not received issue.",
            )

        final_metadata_filter: dict[str, MetadataValue] | None = metadata_filter

        if final_metadata_filter is None and auto_filter:
            final_metadata_filter = {"product": "digital_payments"}

        if final_metadata_filter == {"product": "digital_payments"}:
            retrieved_chunk = RetrievedChunk(
                text=(
                    "Customers may raise a QR payment dispute if a payment "
                    "was deducted but the merchant did not receive confirmation."
                ),
                source="digital_payments.md",
                section="QR Payment Disputes",
                chunk_index=0,
                distance=0.2,
                metadata={
                    "product": "digital_payments",
                    "file_type": "markdown"
                    },
            )
        else:
            retrieved_chunk = RetrievedChunk(
                text=(
                    "Customers who forget their mobile banking password should "
                    "use the forgot password option in the mobile app."
                ),
                source="mobile_app_access.md",
                section="Password Recovery",
                chunk_index=0,
                distance=0.25,
                metadata={
                    "product": "mobile_app",
                    "file_type": "markdown"
                    },
            )

        return RetrievalPipelineResult(
            original_query=query,
            retrieval_query=retrieval_query,
            rewrite_result=rewrite_result,
            metadata_filter=final_metadata_filter,
            retrieval_mode=retrieval_mode,
            rerank_enabled=rerank,
            retrieved_chunks=[retrieved_chunk],
        )


class FakeLLMClient:
    """Fake LLM client for testing without live API calls."""

    def generate(self, prompt: str) -> str:
        assert "Use only the provided context" in prompt

        if "digital_payments.md" in prompt:
            return (
                "The customer may raise a QR payment dispute because the "
                "payment was deducted but the merchant did not receive "
                "confirmation.\n\n"
                "Source: [Source 1] digital_payments.md, QR Payment Disputes"
            )

        return (
            "Customers should use the forgot password option in the mobile app.\n\n"
            "Source: [Source 1] mobile_app_access.md, Password Recovery"
        )


def test_rag_service_returns_grounded_answer() -> None:
    service = BankingRAGService(
        retrieval_pipeline=FakeRetrievalPipeline(),
        llm_client=FakeLLMClient(),
    )

    result = service.answer("I forgot my password.")

    assert isinstance(result, RAGAnswer)
    assert result.question == "I forgot my password."
    assert "forgot password option" in result.answer
    assert len(result.sources) == 1
    assert result.sources[0].source == "mobile_app_access.md"
    assert result.sources[0].section == "Password Recovery"
    assert len(result.retrieved_chunks) == 1
    assert result.retrieval_query == "I forgot my password."
    assert result.metadata_filter is None
    assert result.retrieval_mode == "semantic"
    assert result.rerank_enabled is False
    assert result.query_was_rewritten is False
    assert result.rewrite_reason is None

    assert result.sources[0].file_type == "markdown"
    assert result.sources[0].page_number is None


def test_rag_service_supports_advanced_retrieval_options() -> None:
    service = BankingRAGService(
        retrieval_pipeline=FakeRetrievalPipeline(),
        llm_client=FakeLLMClient(),
    )

    result = service.answer(
        question="money gone shop says no",
        retrieval_mode="hybrid",
        auto_filter=True,
        rewrite_query=True,
        rerank=True,
        candidate_k=6,
    )

    assert result.question == "money gone shop says no"
    assert result.retrieval_query == (
        "QR payment deducted from customer account but merchant "
        "did not receive payment confirmation"
    )
    assert result.metadata_filter == {"product": "digital_payments"}
    assert result.retrieval_mode == "hybrid"
    assert result.rerank_enabled is True
    assert len(result.sources) == 1
    assert result.sources[0].source == "digital_payments.md"
    assert result.sources[0].section == "QR Payment Disputes"
    assert result.retrieved_chunks[0].source == "digital_payments.md"
    assert "QR payment dispute" in result.answer
    assert result.query_was_rewritten is True
    assert result.rewrite_reason == (
        "Detected likely QR payment deducted but merchant not received issue."
    )

    assert result.sources[0].file_type == "markdown"
    assert result.sources[0].page_number is None


class FakePdfRetrievalPipeline:
    """Fake retrieval pipeline that returns a PDF chunk."""

    def retrieve(self, *args, **kwargs):
        retrieved_chunk = RetrievedChunk(
            text="PDF page text about QR disputes.",
            source="digital_payments_policy.pdf",
            section="Page 2",
            chunk_index=1,
            distance=0.31,
            metadata={
                "file_type": "pdf",
                "page_number": 2,
            },
        )

        return RetrievalPipelineResult(
            original_query="Where is the QR dispute policy?",
            retrieval_query="Where is the QR dispute policy?",
            rewrite_result=None,
            metadata_filter=None,
            retrieval_mode="semantic",
            rerank_enabled=False,
            retrieved_chunks=[retrieved_chunk],
        )


def test_rag_service_adds_pdf_page_citation_metadata() -> None:
    service = BankingRAGService(
        retrieval_pipeline=FakePdfRetrievalPipeline(),
        llm_client=FakeLLMClient(),
    )

    result = service.answer("Where is the QR dispute policy?")

    assert result.sources[0].source == "digital_payments_policy.pdf"
    assert result.sources[0].section == "Page 2"
    assert result.sources[0].file_type == "pdf"
    assert result.sources[0].page_number == 2


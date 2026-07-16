from pathlib import Path

from banking_rag.core.schemas import DocumentChunk
from banking_rag.retrieval.retrieval_pipeline import RetrievalPipeline
from banking_rag.retrieval.vector_store import ChromaVectorStore


class FakeEmbeddingModel:
    """Fake embedding model for deterministic pipeline tests."""

    def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def build_pipeline_test_vector_store(tmp_path: Path) -> ChromaVectorStore:
    """Build a small vector store for pipeline tests."""
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="pipeline_test_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text=(
                "Customers may raise a QR payment dispute when the account "
                "was debited but the merchant did not receive confirmation."
            ),
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            metadata={
                "file_type": "markdown",
                "product": "digital_payments",
                "channel": "qr",
                "document_type": "policy",
            },
        ),
        DocumentChunk(
            id="chunk-2",
            text=(
                "Customers who forget their mobile banking password should "
                "use the forgot password option."
            ),
            source="mobile_app_access.md",
            section="Password Recovery",
            chunk_index=0,
            metadata={
                "file_type": "markdown",
                "product": "mobile_app",
                "channel": "mobile_app",
                "document_type": "policy",
            },
        ),
        DocumentChunk(
            id="chunk-3",
            text="Customers can report duplicate card charges.",
            source="card_disputes.md",
            section="Duplicate Card Charges",
            chunk_index=0,
            metadata={
                "file_type": "markdown",
                "product": "cards",
                "channel": "card",
                "document_type": "policy",
            },
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.8, 0.2, 0.0],
        [0.7, 0.3, 0.0],
    ]

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    return vector_store


def test_retrieval_pipeline_applies_rewrite_auto_filter_and_rerank(
    tmp_path: Path,
) -> None:
    vector_store = build_pipeline_test_vector_store(tmp_path)

    pipeline = RetrievalPipeline(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=2,
    )

    result = pipeline.retrieve(
        query="money gone shop says no",
        top_k=1,
        retrieval_mode="hybrid",
        auto_filter=True,
        rewrite_query_enabled=True,
        rerank=True,
        candidate_k=3,
    )

    assert result.original_query == "money gone shop says no"
    assert result.rewrite_result is not None
    assert result.rewrite_result.was_rewritten is True
    assert result.metadata_filter == {"product": "digital_payments"}
    assert result.retrieval_mode == "hybrid"
    assert result.rerank_enabled is True
    assert len(result.retrieved_chunks) == 1
    assert result.retrieved_chunks[0].source == "digital_payments.md"
    assert result.retrieved_chunks[0].section == "QR Payment Disputes"


def test_retrieval_pipeline_manual_filter_overrides_auto_filter(
    tmp_path: Path,
) -> None:
    vector_store = build_pipeline_test_vector_store(tmp_path)

    pipeline = RetrievalPipeline(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=2,
    )

    result = pipeline.retrieve(
        query="app pass forgot",
        top_k=1,
        retrieval_mode="semantic",
        metadata_filter={"product": "cards"},
        auto_filter=True,
        rewrite_query_enabled=True,
        rerank=False,
    )

    assert result.metadata_filter == {"product": "cards"}
    assert len(result.retrieved_chunks) == 1
    assert result.retrieved_chunks[0].source == "card_disputes.md"


def test_retrieval_pipeline_keeps_unclear_query_without_filter(
    tmp_path: Path,
) -> None:
    vector_store = build_pipeline_test_vector_store(tmp_path)

    pipeline = RetrievalPipeline(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=2,
    )

    result = pipeline.retrieve(
        query="what support options are available",
        top_k=2,
        retrieval_mode="semantic",
        auto_filter=True,
        rewrite_query_enabled=True,
        rerank=False,
    )

    assert result.rewrite_result is not None
    assert result.rewrite_result.was_rewritten is False
    assert result.metadata_filter is None
    assert len(result.retrieved_chunks) == 2
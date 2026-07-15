from pathlib import Path

from banking_rag.core.schemas import DocumentChunk
from banking_rag.retrieval.hybrid_retriever import HybridRetriever
from banking_rag.retrieval.vector_store import ChromaVectorStore


class FakeEmbeddingModel:
    """Fake embedding model for deterministic hybrid tests."""

    def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def build_hybrid_test_vector_store(tmp_path: Path) -> ChromaVectorStore:
    """Build a small Chroma store for hybrid retrieval tests."""
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="hybrid_test_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text="General QR payment support information.",
            source="digital_payments.md",
            section="Digital Payment Availability",
            chunk_index=0,
            metadata={
                "file_type": "markdown",
                "product": "digital_payments",
            },
        ),
        DocumentChunk(
            id="chunk-2",
            text=(
                "The internal sample reference code RAAST-P2M-042 refers to "
                "QR payments where the merchant did not receive confirmation."
            ),
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=1,
            metadata={
                "file_type": "markdown",
                "product": "digital_payments",
            },
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.8, 0.2, 0.0],
    ]

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    return vector_store


def test_hybrid_retriever_uses_keyword_score_for_exact_code(
    tmp_path: Path,
) -> None:
    vector_store = build_hybrid_test_vector_store(tmp_path)

    retriever = HybridRetriever(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=1,
        semantic_weight=0.3,
        keyword_weight=0.7,
    )

    results = retriever.retrieve(
        query="What does RAAST-P2M-042 mean?",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].section == "QR Payment Disputes"
    assert results[0].keyword_score > 0
    assert results[0].hybrid_score > 0


def test_hybrid_retriever_respects_metadata_filter(
    tmp_path: Path,
) -> None:
    vector_store = build_hybrid_test_vector_store(tmp_path)

    retriever = HybridRetriever(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=2,
    )

    results = retriever.retrieve(
        query="What does RAAST-P2M-042 mean?",
        top_k=2,
        metadata_filter={"product": "digital_payments"},
    )

    assert len(results) == 2
    assert all(
        result.metadata["product"] == "digital_payments"
        for result in results
    )
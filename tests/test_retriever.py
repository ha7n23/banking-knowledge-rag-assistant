from pathlib import Path

import pytest

from banking_rag.core.exceptions import RetrievalError
from banking_rag.core.schemas import DocumentChunk
from banking_rag.retrieval.retriever import KnowledgeRetriever
from banking_rag.retrieval.vector_store import ChromaVectorStore


class FakeEmbeddingModel:
    """Small fake embedding model for deterministic retriever tests."""

    def embed_query(self, query: str) -> list[float]:
        """Return deterministic embeddings based on the query text."""
        if "password" in query.lower():
            return [0.0, 1.0, 0.0]

        return [1.0, 0.0, 0.0]


def build_test_vector_store(tmp_path: Path) -> ChromaVectorStore:
    """Build a small test Chroma store with deterministic embeddings."""
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="retriever_test_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text="Customers may raise a QR payment dispute.",
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            metadata={"file_type": "markdown"},
        ),
        DocumentChunk(
            id="chunk-2",
            text="Customers can reset their mobile banking password.",
            source="mobile_app_access.md",
            section="Password Recovery",
            chunk_index=0,
            metadata={"file_type": "markdown"},
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    return vector_store


def test_retriever_returns_relevant_chunks(tmp_path: Path) -> None:
    vector_store = build_test_vector_store(tmp_path)

    retriever = KnowledgeRetriever(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=1,
    )

    results = retriever.retrieve("How do I reset my password?")

    assert len(results) == 1
    assert results[0].source == "mobile_app_access.md"
    assert results[0].section == "Password Recovery"
    assert "password" in results[0].text.lower()


def test_retriever_rejects_empty_query(tmp_path: Path) -> None:
    vector_store = build_test_vector_store(tmp_path)

    retriever = KnowledgeRetriever(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=1,
    )

    with pytest.raises(RetrievalError):
        retriever.retrieve("   ")


def test_retriever_fails_when_vector_store_is_empty(tmp_path: Path) -> None:
    empty_vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "empty_chroma",
        collection_name="empty_retriever_test_collection",
    )
    empty_vector_store.reset_collection()

    retriever = KnowledgeRetriever(
        embedding_model=FakeEmbeddingModel(),
        vector_store=empty_vector_store,
        default_top_k=1,
    )

    with pytest.raises(RetrievalError):
        retriever.retrieve("QR payment dispute")
from pathlib import Path

from banking_rag.core.schemas import DocumentChunk
from banking_rag.retrieval.vector_store import ChromaVectorStore


def test_chroma_vector_store_adds_and_counts_chunks(tmp_path: Path) -> None:
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="test_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text="Customers can raise QR payment disputes.",
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            metadata={"file_type": "markdown"},
        )
    ]

    embeddings = [[0.1, 0.2, 0.3]]

    vector_store.add_chunks(chunks=chunks, embeddings=embeddings)

    assert vector_store.count() == 1


def test_chroma_vector_store_query_returns_results(tmp_path: Path) -> None:
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="test_query_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text="Customers can raise QR payment disputes.",
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

    vector_store.add_chunks(chunks=chunks, embeddings=embeddings)

    results = vector_store.query(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert results["documents"][0][0] == "Customers can raise QR payment disputes."
    assert results["metadatas"][0][0]["source"] == "digital_payments.md"

def test_chroma_vector_store_query_supports_metadata_filter(tmp_path: Path) -> None:
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="test_metadata_filter_collection",
    )
    vector_store.reset_collection()

    chunks = [
        DocumentChunk(
            id="chunk-1",
            text="Customers can raise QR payment disputes.",
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
        [0.9, 0.1, 0.0],
    ]

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    results = vector_store.query(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=2,
        metadata_filter={"product": "cards"},
    )

    assert len(results["documents"][0]) == 1
    assert results["metadatas"][0][0]["source"] == "card_disputes.md"
    assert results["metadatas"][0][0]["product"] == "cards"
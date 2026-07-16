import json
from pathlib import Path

from banking_rag.core.schemas import DocumentChunk
from banking_rag.retrieval.retrieval_pipeline import RetrievalPipeline
from banking_rag.retrieval.vector_store import ChromaVectorStore
from banking_rag.services.advanced_evaluation_service import (
    AdvancedRetrievalEvaluationService,
)


class FakeEmbeddingModel:
    """Fake embedding model for deterministic advanced evaluation tests."""

    def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def build_advanced_eval_vector_store(tmp_path: Path) -> ChromaVectorStore:
    """Build a small vector store for advanced evaluation tests."""
    vector_store = ChromaVectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="advanced_eval_test_collection",
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
            },
        ),
        DocumentChunk(
            id="chunk-2",
            text="Customers can reset forgotten mobile banking passwords.",
            source="mobile_app_access.md",
            section="Password Recovery",
            chunk_index=0,
            metadata={
                "file_type": "markdown",
                "product": "mobile_app",
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


def test_advanced_evaluation_service_uses_pipeline(
    tmp_path: Path,
) -> None:
    evaluation_file = tmp_path / "advanced_eval.json"
    evaluation_file.write_text(
        json.dumps(
            [
                {
                    "question": "money gone shop says no",
                    "expected_top_source": "digital_payments.md",
                    "expected_top_section": "QR Payment Disputes",
                    "expected_behavior": "Retrieve QR payment dispute.",
                    "expected_answer_type": "direct_answer",
                    "must_not_include": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    vector_store = build_advanced_eval_vector_store(tmp_path)

    pipeline = RetrievalPipeline(
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
        default_top_k=2,
    )

    service = AdvancedRetrievalEvaluationService(
        retrieval_pipeline=pipeline,
        evaluation_file=evaluation_file,
    )

    summary = service.run(
        top_k=1,
        retrieval_mode="hybrid",
        auto_filter=True,
        rewrite_query_enabled=True,
        rerank=True,
        candidate_k=2,
    )

    assert summary.total == 1
    assert summary.top_1_passed == 1
    assert summary.top_k_passed == 1
    assert summary.failed_top_k == 0
    assert summary.results[0].expected_rank == 1
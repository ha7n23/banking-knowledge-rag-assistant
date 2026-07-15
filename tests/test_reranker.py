from banking_rag.core.schemas import RetrievedChunk
from banking_rag.retrieval.reranker import SimpleReranker


def test_reranker_can_promote_exact_keyword_match() -> None:
    chunks = [
        RetrievedChunk(
            text="General QR payment support information.",
            source="digital_payments.md",
            section="Digital Payment Availability",
            chunk_index=0,
            distance=0.2,
            metadata={},
        ),
        RetrievedChunk(
            text=(
                "The internal sample reference code RAAST-P2M-042 refers "
                "to QR payments where the merchant did not receive confirmation."
            ),
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=1,
            distance=0.5,
            metadata={},
        ),
    ]

    reranker = SimpleReranker(
        semantic_weight=0.1,
        keyword_weight=0.8,
        section_weight=0.1,
    )

    results = reranker.rerank(
        query="What does RAAST-P2M-042 mean?",
        chunks=chunks,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].section == "QR Payment Disputes"
    assert results[0].original_rank == 2
    assert results[0].rerank_keyword_score > 0
    assert results[0].rerank_score > 0


def test_reranker_returns_empty_list_for_no_chunks() -> None:
    reranker = SimpleReranker()

    results = reranker.rerank(
        query="test query",
        chunks=[],
        top_k=3,
    )

    assert results == []


def test_reranker_respects_top_k() -> None:
    chunks = [
        RetrievedChunk(
            text="Password reset support.",
            source="mobile_app_access.md",
            section="Password Recovery",
            chunk_index=0,
            distance=0.2,
            metadata={},
        ),
        RetrievedChunk(
            text="Registered mobile number support.",
            source="mobile_app_access.md",
            section="Registered Mobile Number Issues",
            chunk_index=1,
            distance=0.3,
            metadata={},
        ),
    ]

    reranker = SimpleReranker()

    results = reranker.rerank(
        query="password reset",
        chunks=chunks,
        top_k=1,
    )

    assert len(results) == 1
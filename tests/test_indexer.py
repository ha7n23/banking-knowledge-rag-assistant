from banking_rag.ingestion.indexer import KnowledgeBaseIndexer


def test_indexer_builds_chunks_from_sample_documents() -> None:
    indexer = KnowledgeBaseIndexer()

    chunks = indexer.build_chunks()

    assert len(chunks) == 9

    sources = {chunk.source for chunk in chunks}
    sections = {chunk.section for chunk in chunks}

    assert "digital_payments.md" in sources
    assert "mobile_app_access.md" in sources
    assert "card_disputes.md" in sources

    assert "QR Payment Disputes" in sections
    assert "Password Recovery" in sections
    assert "Duplicate Card Charges" in sections
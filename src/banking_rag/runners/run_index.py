from banking_rag.ingestion.indexer import KnowledgeBaseIndexer


def main() -> None:
    """Build the Chroma knowledge base from raw documents."""
    print("Building banking knowledge base...")

    indexer = KnowledgeBaseIndexer()
    indexed_count = indexer.index(reset=True)

    print(f"Indexed {indexed_count} chunks into Chroma.")


if __name__ == "__main__":
    main()
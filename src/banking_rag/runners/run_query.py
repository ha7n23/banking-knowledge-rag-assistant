from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.retrieval.retriever import KnowledgeRetriever

from banking_rag.core.schemas import MetadataValue

from banking_rag.retrieval.filter_router import infer_metadata_filter

from banking_rag.retrieval.hybrid_retriever import HybridRetriever

from banking_rag.retrieval.reranker import SimpleReranker

from banking_rag.retrieval.query_rewriter import rewrite_query

DEFAULT_QUERY = (
    "What should happen if my QR payment was deducted "
    "but the merchant did not receive it?"
)


def parse_args() -> ArgumentParser:
    """Create the command-line argument parser."""
    parser = ArgumentParser(
        description="Retrieve relevant banking knowledge chunks for a query."
    )

    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="User question to retrieve relevant chunks for.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to retrieve.",
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Optional source file filter, for example digital_payments.md.",
    )

    parser.add_argument(
        "--product",
        type=str,
        default=None,
        help="Optional product filter, for example digital_payments, cards, mobile_app.",
    )

    parser.add_argument(
        "--channel",
        type=str,
        default=None,
        help="Optional channel filter, for example qr, card, mobile_app.",
    )

    parser.add_argument(
        "--document-type",
        type=str,
        default=None,
        help="Optional document type filter, for example policy.",
    )

    parser.add_argument(
        "--auto-filter",
        action="store_true",
        help="Automatically infer a metadata filter from the query.",
    )

    parser.add_argument(
        "--retrieval-mode",
        choices=["semantic", "hybrid"],
        default="semantic",
        help="Retrieval mode to use.",
    )

    parser.add_argument(
        "--rerank",
        action="store_true",
        help="Rerank retrieved candidate chunks before printing final results.",
    )

    parser.add_argument(
        "--candidate-k",
        type=int,
        default=8,
        help="Number of candidate chunks to retrieve before reranking.",
    )

    parser.add_argument(
        "--rewrite-query",
        action="store_true",
        help="Conservatively rewrite messy user queries before retrieval.",
    )

    return parser

def build_metadata_filter(args: object) -> dict[str, MetadataValue] | None:
    """Build a metadata filter from CLI arguments."""
    filters: dict[str, MetadataValue] = {}

    source = getattr(args, "source", None)
    product = getattr(args, "product", None)
    channel = getattr(args, "channel", None)
    document_type = getattr(args, "document_type", None)

    if source:
        filters["source"] = source

    if product:
        filters["product"] = product

    if channel:
        filters["channel"] = channel

    if document_type:
        filters["document_type"] = document_type

    return filters or None


def main() -> None:
    """Run retrieval for a user query and print ranked chunks."""
    parser = parse_args()
    args = parser.parse_args()

    query = args.query
    rewrite_result = None

    if args.rewrite_query:
        rewrite_result = rewrite_query(args.query)
        query = rewrite_result.rewritten_query

    metadata_filter = build_metadata_filter(args)

    if metadata_filter is None and args.auto_filter:
        metadata_filter = infer_metadata_filter(query)

    if args.retrieval_mode == "hybrid":
        retriever = HybridRetriever()
    else:
        retriever = KnowledgeRetriever()

    retrieval_top_k = args.top_k

    if args.rerank:
        retrieval_top_k = max(args.top_k, args.candidate_k)

    retrieved_chunks = retriever.retrieve(
        query=query,
        top_k=retrieval_top_k,
        metadata_filter=metadata_filter,
    )

    if args.rerank:
        reranker = SimpleReranker()
        retrieved_chunks = reranker.rerank(
            query=query,
            chunks=retrieved_chunks,
            top_k=args.top_k,
        )

    print("\n" + "=" * 80)
    print(f"QUERY: {args.query}")
    if rewrite_result is not None:
        print(f"REWRITTEN QUERY: {rewrite_result.rewritten_query}")
        print(f"QUERY WAS REWRITTEN: {rewrite_result.was_rewritten}")
        print(f"REWRITE REASON: {rewrite_result.reason}")
    print("=" * 80)

    if metadata_filter:
        print(f"METADATA FILTER: {metadata_filter}")

    for rank, chunk in enumerate(retrieved_chunks, start=1):
        print(f"\nRESULT {rank}")
        print("-" * 80)
        print(f"Source: {chunk.source}")
        print(f"Section: {chunk.section}")
        print(f"Chunk index: {chunk.chunk_index}")
        print(f"Distance: {chunk.distance:.4f}")

        semantic_rank = getattr(chunk, "semantic_rank", None)
        keyword_score = getattr(chunk, "keyword_score", None)
        hybrid_score = getattr(chunk, "hybrid_score", None)

        if semantic_rank is not None:
            print(f"Semantic rank: {semantic_rank}")

        if keyword_score is not None:
            print(f"Keyword score: {keyword_score:.4f}")

        if hybrid_score is not None:
            print(f"Hybrid score: {hybrid_score:.4f}")

        original_rank = getattr(chunk, "original_rank", None)
        rerank_keyword_score = getattr(chunk, "rerank_keyword_score", None)
        rerank_section_score = getattr(chunk, "rerank_section_score", None)
        rerank_score = getattr(chunk, "rerank_score", None)

        if original_rank is not None:
            print(f"Original rank: {original_rank}")

        if rerank_keyword_score is not None:
            print(f"Rerank keyword score: {rerank_keyword_score:.4f}")

        if rerank_section_score is not None:
            print(f"Rerank section score: {rerank_section_score:.4f}")

        if rerank_score is not None:
            print(f"Rerank score: {rerank_score:.4f}")

        print("\nChunk text:")
        print(chunk.text)


if __name__ == "__main__":
    main()
from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.retrieval.retriever import KnowledgeRetriever

from banking_rag.core.schemas import MetadataValue


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

    metadata_filter = build_metadata_filter(args)

    retriever = KnowledgeRetriever()
    retrieved_chunks = retriever.retrieve(
        query=args.query,
        top_k=args.top_k,
        metadata_filter=metadata_filter,
    )

    print("\n" + "=" * 80)
    print(f"QUERY: {args.query}")
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
        print("\nChunk text:")
        print(chunk.text)


if __name__ == "__main__":
    main()
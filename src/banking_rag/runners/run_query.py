from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.retrieval.retriever import KnowledgeRetriever


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

    return parser


def main() -> None:
    """Run retrieval for a user query and print ranked chunks."""
    parser = parse_args()
    args = parser.parse_args()

    retriever = KnowledgeRetriever()
    retrieved_chunks = retriever.retrieve(
        query=args.query,
        top_k=args.top_k,
    )

    print("\n" + "=" * 80)
    print(f"QUERY: {args.query}")
    print("=" * 80)

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
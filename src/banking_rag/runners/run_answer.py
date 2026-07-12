from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.services.rag_service import BankingRAGService


DEFAULT_QUERY = (
    "What is the exact refund timeline for a failed QR payment?"
)


def parse_args() -> ArgumentParser:
    """Create the command-line argument parser."""
    parser = ArgumentParser(
        description="Generate a grounded RAG answer for a banking question."
    )

    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="User question to answer.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to retrieve.",
    )

    return parser


def main() -> None:
    """Run the full RAG pipeline and print the answer."""
    parser = parse_args()
    args = parser.parse_args()

    rag_service = BankingRAGService()
    result = rag_service.answer(
        question=args.query,
        top_k=args.top_k,
    )

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(result.question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result.answer)

    print("\n" + "=" * 80)
    print("RETRIEVED SOURCES")
    print("=" * 80)

    for index, source in enumerate(result.sources, start=1):
        print(
            f"{index}. {source.source} | "
            f"{source.section} | "
            f"chunk {source.chunk_index} | "
            f"distance {source.distance:.4f}"
        )


if __name__ == "__main__":
    main()
from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.services.evaluation_service import RetrievalEvaluationService


def parse_args() -> ArgumentParser:
    """Create the command-line argument parser."""
    parser = ArgumentParser(
        description="Run retrieval evaluation for the Banking RAG Assistant."
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to retrieve for each evaluation question.",
    )

    return parser


def main() -> None:
    """Run retrieval evaluation and print results."""
    parser = parse_args()
    args = parser.parse_args()

    service = RetrievalEvaluationService()
    summary = service.run(top_k=args.top_k)

    print("\n" + "=" * 80)
    print("RETRIEVAL EVALUATION")
    print("=" * 80)

    for index, result in enumerate(summary.results, start=1):
        status = "PASS" if result.passed else "FAIL"

        print(f"\nQuestion {index}: {status}")
        print("-" * 80)
        print(f"Question: {result.question}")
        print(f"Expected source: {result.expected_top_source}")
        print(f"Expected section: {result.expected_top_section}")
        print(f"Retrieved source: {result.retrieved_top_source}")
        print(f"Retrieved section: {result.retrieved_top_section}")
        print(f"Distance: {result.retrieved_distance:.4f}")
        print(f"Expected behavior: {result.expected_behavior}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Total: {summary.total}")

    if summary.failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
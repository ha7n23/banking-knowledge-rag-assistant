from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.services.advanced_evaluation_service import (
    AdvancedRetrievalEvaluationService,
)


def parse_args() -> ArgumentParser:
    """Create command-line parser for advanced retrieval evaluation."""
    parser = ArgumentParser(
        description="Run advanced retrieval evaluation."
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to return after retrieval.",
    )

    parser.add_argument(
        "--retrieval-mode",
        choices=["semantic", "hybrid"],
        default="hybrid",
        help="Retrieval mode to evaluate.",
    )

    parser.add_argument(
        "--auto-filter",
        action="store_true",
        help="Enable automatic metadata filter inference.",
    )

    parser.add_argument(
        "--rewrite-query",
        action="store_true",
        help="Enable conservative query rewriting.",
    )

    parser.add_argument(
        "--rerank",
        action="store_true",
        help="Enable lightweight reranking.",
    )

    parser.add_argument(
        "--candidate-k",
        type=int,
        default=8,
        help="Number of candidate chunks to retrieve before reranking.",
    )

    return parser


def main() -> None:
    """Run advanced retrieval evaluation and print results."""
    parser = parse_args()
    args = parser.parse_args()

    service = AdvancedRetrievalEvaluationService()

    summary = service.run(
        top_k=args.top_k,
        retrieval_mode=args.retrieval_mode,
        auto_filter=args.auto_filter,
        rewrite_query_enabled=args.rewrite_query,
        rerank=args.rerank,
        candidate_k=args.candidate_k,
    )

    print("\n" + "=" * 80)
    print("ADVANCED RETRIEVAL EVALUATION")
    print("=" * 80)
    print(f"Retrieval mode: {args.retrieval_mode}")
    print(f"Auto-filter: {args.auto_filter}")
    print(f"Rewrite query: {args.rewrite_query}")
    print(f"Rerank: {args.rerank}")
    print(f"Candidate-k: {args.candidate_k}")

    for index, result in enumerate(summary.results, start=1):
        status = "PASS" if result.passed else "FAIL"

        print(f"\nQuestion {index}: {status}")
        print("-" * 80)
        print(f"Question: {result.question}")
        print(f"Expected source: {result.expected_top_source}")
        print(f"Expected section: {result.expected_top_section}")
        print(f"Retrieved top source: {result.retrieved_top_source}")
        print(f"Retrieved top section: {result.retrieved_top_section}")
        print(f"Top distance: {result.retrieved_distance:.4f}")
        print(f"Expected rank in top-k: {result.expected_rank}")
        print(f"Top-1 passed: {result.top_1_passed}")
        print(f"Top-k passed: {result.top_k_passed}")
        print(f"Expected behavior: {result.expected_behavior}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Top-1 passed: {summary.top_1_passed}")
    print(f"Top-k passed: {summary.top_k_passed}")
    print(f"Failed top-k: {summary.failed_top_k}")
    print(f"Total: {summary.total}")

    if summary.failed_top_k > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
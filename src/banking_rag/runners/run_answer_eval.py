from argparse import ArgumentParser

from banking_rag.core.config import TOP_K
from banking_rag.services.answer_evaluation_service import (
    AnswerEvaluationService,
)

from banking_rag.services.evaluation_report_writer import (
    AnswerEvaluationReportWriter,
)


def parse_args() -> ArgumentParser:
    """Create command-line parser for answer evaluation."""
    parser = ArgumentParser(
        description="Run generated answer evaluation for the RAG assistant."
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to retrieve for each question.",
    )

    parser.add_argument(
        "--retrieval-mode",
        choices=["semantic", "hybrid"],
        default="semantic",
        help="Retrieval mode to use.",
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

    parser.add_argument(
        "--report-name",
        default="answer_eval_latest",
        help="Base filename for saved evaluation reports.",
    )

    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip writing JSON and Markdown evaluation reports.",
    )

    return parser


def main() -> None:
    """Run answer evaluation and print results."""
    parser = parse_args()
    args = parser.parse_args()

    service = AnswerEvaluationService()

    summary = service.run(
        top_k=args.top_k,
        retrieval_mode=args.retrieval_mode,
        auto_filter=args.auto_filter,
        rewrite_query=args.rewrite_query,
        rerank=args.rerank,
        candidate_k=args.candidate_k,
    )

    print("\n" + "=" * 80)
    print("ANSWER EVALUATION")
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
        print(f"Expected answer type: {result.expected_answer_type}")
        print(f"Expected behavior: {result.expected_behavior}")
        print(f"Has sources: {result.has_sources}")
        print(
            "Citation validation passed: "
            f"{result.citation_validation_passed}"
        )
        print(f"Cited source numbers: {result.cited_source_numbers}")

        if result.invalid_source_numbers:
            print(
                "Invalid source numbers: "
                f"{result.invalid_source_numbers}"
            )

        print(
            "No-answer language detected: "
            f"{result.no_answer_language_detected}"
        )

        if result.forbidden_terms_found:
            print(
                "Forbidden terms found: "
                f"{', '.join(result.forbidden_terms_found)}"
            )

        print("\nAnswer:")
        print(result.answer)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Total: {summary.total}")

    if not args.skip_report:
        report_writer = AnswerEvaluationReportWriter()
        json_path, markdown_path = report_writer.write(
            summary=summary,
            report_name=args.report_name,
        )

        print("\n" + "=" * 80)
        print("REPORTS WRITTEN")
        print("=" * 80)
        print(f"JSON report: {json_path}")
        print(f"Markdown report: {markdown_path}")

    if summary.failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
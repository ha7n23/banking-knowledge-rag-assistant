import json
from pathlib import Path

from banking_rag.core.config import EVALUATION_FILE, TOP_K
from banking_rag.core.schemas import (
    EvaluationQuestion,
    EvaluationSummary,
    RetrievalEvaluationResult,
    RetrievedChunk,
)
from banking_rag.retrieval.retriever import KnowledgeRetriever


class RetrievalEvaluationService:
    """Evaluates whether retrieval returns expected chunks."""

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        evaluation_file: Path = EVALUATION_FILE,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.evaluation_file = evaluation_file

    def load_questions(self) -> list[EvaluationQuestion]:
        """Load evaluation questions from JSON."""
        with self.evaluation_file.open("r", encoding="utf-8") as file:
            raw_questions = json.load(file)

        return [EvaluationQuestion(**item) for item in raw_questions]

    def evaluate_question(
        self,
        evaluation_question: EvaluationQuestion,
        top_k: int = TOP_K,
    ) -> RetrievalEvaluationResult:
        """Evaluate retrieval for one question."""
        retrieved_chunks = self.retriever.retrieve(
            query=evaluation_question.question,
            top_k=top_k,
        )

        top_chunk = self._get_top_chunk(retrieved_chunks)
        expected_rank = self._find_expected_rank(
            retrieved_chunks=retrieved_chunks,
            expected_source=evaluation_question.expected_top_source,
            expected_section=evaluation_question.expected_top_section,
        )

        top_1_passed = expected_rank == 1
        top_k_passed = expected_rank is not None

        return RetrievalEvaluationResult(
            question=evaluation_question.question,
            expected_top_source=evaluation_question.expected_top_source,
            expected_top_section=evaluation_question.expected_top_section,
            retrieved_top_source=top_chunk.source,
            retrieved_top_section=top_chunk.section,
            retrieved_distance=top_chunk.distance,
            expected_behavior=evaluation_question.expected_behavior,
            expected_answer_type=evaluation_question.expected_answer_type,
            must_not_include=evaluation_question.must_not_include,
            expected_rank=expected_rank,
            top_1_passed=top_1_passed,
            top_k_passed=top_k_passed,
            passed=top_k_passed,
        )

    def run(self, top_k: int = TOP_K) -> EvaluationSummary:
        """Run retrieval evaluation for all questions."""
        questions = self.load_questions()

        results = [
            self.evaluate_question(
                evaluation_question=question,
                top_k=top_k,
            )
            for question in questions
        ]

        top_1_passed = sum(1 for result in results if result.top_1_passed)
        top_k_passed = sum(1 for result in results if result.top_k_passed)
        failed_top_k = len(results) - top_k_passed

        return EvaluationSummary(
            total=len(results),
            top_1_passed=top_1_passed,
            top_k_passed=top_k_passed,
            failed_top_k=failed_top_k,
            results=results,
        )

    def _get_top_chunk(
        self,
        retrieved_chunks: list[RetrievedChunk],
    ) -> RetrievedChunk:
        """Return the top retrieved chunk or an empty placeholder."""
        if retrieved_chunks:
            return retrieved_chunks[0]

        return RetrievedChunk(
            text="",
            source="",
            section="",
            chunk_index=0,
            distance=float("inf"),
            metadata={},
        )

    def _find_expected_rank(
        self,
        retrieved_chunks: list[RetrievedChunk],
        expected_source: str,
        expected_section: str,
    ) -> int | None:
        """Find the rank of the expected source and section in retrieved chunks."""
        for rank, chunk in enumerate(retrieved_chunks, start=1):
            if (
                chunk.source == expected_source
                and chunk.section == expected_section
            ):
                return rank

        return None 
    
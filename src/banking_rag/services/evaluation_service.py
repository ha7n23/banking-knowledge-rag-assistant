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
    """Evaluates whether retrieval returns expected top chunks."""

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

        if not retrieved_chunks:
            top_chunk = RetrievedChunk(
                text="",
                source="",
                section="",
                chunk_index=0,
                distance=float("inf"),
                metadata={},
            )
        else:
            top_chunk = retrieved_chunks[0]

        passed = (
            top_chunk.source == evaluation_question.expected_top_source
            and top_chunk.section == evaluation_question.expected_top_section
        )

        return RetrievalEvaluationResult(
            question=evaluation_question.question,
            expected_top_source=evaluation_question.expected_top_source,
            expected_top_section=evaluation_question.expected_top_section,
            retrieved_top_source=top_chunk.source,
            retrieved_top_section=top_chunk.section,
            retrieved_distance=top_chunk.distance,
            expected_behavior=evaluation_question.expected_behavior,
            passed=passed,
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

        passed = sum(1 for result in results if result.passed)
        failed = len(results) - passed

        return EvaluationSummary(
            total=len(results),
            passed=passed,
            failed=failed,
            results=results,
        )
import json
from pathlib import Path
from typing import Protocol

from banking_rag.core.config import EVALUATION_FILE, TOP_K
from banking_rag.core.schemas import (
    AnswerEvaluationResult,
    AnswerEvaluationSummary,
    EvaluationQuestion,
    MetadataValue,
    RAGAnswer,
    RetrievalMode,
)
from banking_rag.services.citation_validation_service import (
    CitationValidationService,
)
from banking_rag.services.rag_service import BankingRAGService


class AnswerServiceProtocol(Protocol):
    """Protocol for any service that can answer RAG questions."""

    def answer(
        self,
        question: str,
        top_k: int | None = None,
        retrieval_mode: RetrievalMode = "semantic",
        metadata_filter: dict[str, MetadataValue] | None = None,
        auto_filter: bool = False,
        rewrite_query: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> RAGAnswer:
        """Generate a grounded RAG answer."""
        ...


class AnswerEvaluationService:
    """Evaluates generated RAG answers for grounding, citations, and safety."""

    def __init__(
        self,
        answer_service: AnswerServiceProtocol | None = None,
        evaluation_file: Path = EVALUATION_FILE,
        citation_validation_service: CitationValidationService | None = None,
    ) -> None:
        self.answer_service = answer_service or BankingRAGService()
        self.evaluation_file = evaluation_file
        self.citation_validation_service = (
            citation_validation_service or CitationValidationService()
        )

    def load_questions(self) -> list[EvaluationQuestion]:
        """Load answer evaluation questions from JSON."""
        with self.evaluation_file.open("r", encoding="utf-8") as file:
            raw_questions = json.load(file)

        return [EvaluationQuestion(**item) for item in raw_questions]

    def evaluate_question(
        self,
        evaluation_question: EvaluationQuestion,
        top_k: int = TOP_K,
        retrieval_mode: RetrievalMode = "semantic",
        auto_filter: bool = False,
        rewrite_query: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> AnswerEvaluationResult:
        """Evaluate one generated RAG answer."""
        rag_answer = self.answer_service.answer(
            question=evaluation_question.question,
            top_k=top_k,
            retrieval_mode=retrieval_mode,
            auto_filter=auto_filter,
            rewrite_query=rewrite_query,
            rerank=rerank,
            candidate_k=candidate_k,
        )

        forbidden_terms_found = self._find_forbidden_terms(
            answer=rag_answer.answer,
            forbidden_terms=evaluation_question.must_not_include,
        )

        has_sources = len(rag_answer.sources) > 0

        citation_validation_result = self.citation_validation_service.validate(
            answer=rag_answer.answer,
            source_count=len(rag_answer.sources),
        )

        no_answer_language_detected = self._detect_no_answer_language(
            rag_answer.answer
        )

        passed = self._decide_passed(
            expected_answer_type=evaluation_question.expected_answer_type,
            forbidden_terms_found=forbidden_terms_found,
            has_sources=has_sources,
            no_answer_language_detected=no_answer_language_detected,
            citation_validation_passed=citation_validation_result.passed,
        )

        return AnswerEvaluationResult(
            question=evaluation_question.question,
            expected_answer_type=evaluation_question.expected_answer_type,
            expected_behavior=evaluation_question.expected_behavior,
            answer=rag_answer.answer,
            has_sources=has_sources,
            forbidden_terms_found=forbidden_terms_found,
            no_answer_language_detected=no_answer_language_detected,
            cited_source_numbers=citation_validation_result.cited_source_numbers,
            invalid_source_numbers=citation_validation_result.invalid_source_numbers,
            citation_validation_passed=citation_validation_result.passed,
            passed=passed,
        )

    def run(
        self,
        top_k: int = TOP_K,
        retrieval_mode: RetrievalMode = "semantic",
        auto_filter: bool = False,
        rewrite_query: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> AnswerEvaluationSummary:
        """Run answer evaluation for all questions."""
        questions = self.load_questions()

        results = [
            self.evaluate_question(
                evaluation_question=question,
                top_k=top_k,
                retrieval_mode=retrieval_mode,
                auto_filter=auto_filter,
                rewrite_query=rewrite_query,
                rerank=rerank,
                candidate_k=candidate_k,
            )
            for question in questions
        ]

        passed = sum(1 for result in results if result.passed)
        failed = len(results) - passed

        return AnswerEvaluationSummary(
            total=len(results),
            passed=passed,
            failed=failed,
            results=results,
        )

    def _find_forbidden_terms(
        self,
        answer: str,
        forbidden_terms: list[str],
    ) -> list[str]:
        """Find unsupported forbidden terms in an answer."""
        answer_lower = answer.lower()

        return [
            term
            for term in forbidden_terms
            if term.lower() in answer_lower
        ]

    def _detect_no_answer_language(self, answer: str) -> bool:
        """Detect whether the answer admits insufficient information."""
        answer_lower = answer.lower()

        no_answer_phrases = [
            "do not contain enough information",
            "does not contain enough information",
            "not enough information",
            "provided documents do not specify",
            "provided documents do not contain",
            "cannot specify",
            "cannot determine",
        ]

        return any(phrase in answer_lower for phrase in no_answer_phrases)

    def _decide_passed(
        self,
        expected_answer_type: str,
        forbidden_terms_found: list[str],
        has_sources: bool,
        no_answer_language_detected: bool,
        citation_validation_passed: bool,
    ) -> bool:
        """Decide whether an answer passes basic grounding and safety checks."""
        if forbidden_terms_found:
            return False

        if not has_sources:
            return False

        if not citation_validation_passed:
            return False

        if expected_answer_type == "no_answer":
            return no_answer_language_detected

        return True
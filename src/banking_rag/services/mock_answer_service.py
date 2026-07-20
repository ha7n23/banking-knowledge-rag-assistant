from banking_rag.core.schemas import (
    MetadataValue,
    RAGAnswer,
    RetrievalMode,
    SourceReference,
)


class MockAnswerService:
    """
    Deterministic answer service for offline evaluation.

    This is useful for testing the evaluation pipeline, citation validation,
    report writing, and quality gates without calling a live LLM.
    """

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
        """Return a deterministic grounded answer for known eval questions."""
        normalized_question = question.lower()

        if "refund timeline" in normalized_question:
            return self._refund_timeline_answer(question)

        if "forgot my mobile banking password" in normalized_question:
            return self._password_recovery_answer(question)

        if "charged twice" in normalized_question:
            return self._duplicate_card_charge_answer(question)

        if "qr payment" in normalized_question or "merchant did not receive" in normalized_question:
            return self._qr_dispute_answer(question)

        return self._generic_no_answer(question)

    def _qr_dispute_answer(self, question: str) -> RAGAnswer:
        """Return deterministic QR dispute answer."""
        return RAGAnswer(
            question=question,
            answer=(
                "If a QR payment was deducted but the merchant did not receive "
                "the funds, the customer may raise a dispute. The bank reviews "
                "transaction status, merchant confirmation, settlement records, "
                "and channel logs.\n\n"
                "Source: [Source 1] digital_payments.md, QR Payment Disputes."
            ),
            sources=[
                SourceReference(
                    source="digital_payments.md",
                    section="QR Payment Disputes",
                    chunk_index=0,
                    distance=0.0,
                    file_type="markdown",
                    page_number=None,
                )
            ],
            retrieved_chunks=[],
            retrieval_query=question,
            retrieval_mode="hybrid",
            rerank_enabled=True,
        )

    def _refund_timeline_answer(self, question: str) -> RAGAnswer:
        """Return deterministic no-answer refund timeline answer."""
        return RAGAnswer(
            question=question,
            answer=(
                "The provided documents do not contain enough information "
                "to specify an exact refund timeline for a failed QR payment.\n\n"
                "Source: [Source 1] digital_payments.md, QR Payment Disputes."
            ),
            sources=[
                SourceReference(
                    source="digital_payments.md",
                    section="QR Payment Disputes",
                    chunk_index=0,
                    distance=0.0,
                    file_type="markdown",
                    page_number=None,
                )
            ],
            retrieved_chunks=[],
            retrieval_query=question,
            retrieval_mode="hybrid",
            rerank_enabled=True,
        )

    def _password_recovery_answer(self, question: str) -> RAGAnswer:
        """Return deterministic password recovery answer."""
        return RAGAnswer(
            question=question,
            answer=(
                "Customers who forget their mobile banking password should use "
                "the forgot password option in the mobile app. They may need "
                "to verify their registered mobile number before setting a new "
                "password.\n\n"
                "Source: [Source 1] mobile_app_access.md, Password Recovery."
            ),
            sources=[
                SourceReference(
                    source="mobile_app_access.md",
                    section="Password Recovery",
                    chunk_index=0,
                    distance=0.0,
                    file_type="markdown",
                    page_number=None,
                )
            ],
            retrieved_chunks=[],
            retrieval_query=question,
            retrieval_mode="hybrid",
            rerank_enabled=True,
        )

    def _duplicate_card_charge_answer(self, question: str) -> RAGAnswer:
        """Return deterministic duplicate card charge answer."""
        return RAGAnswer(
            question=question,
            answer=(
                "Customers can report duplicate card transactions where the "
                "same merchant payment is charged more than once. These cases "
                "are reviewed using card transaction logs, merchant records, "
                "and settlement information.\n\n"
                "Source: [Source 1] card_disputes.md, Duplicate Card Charges."
            ),
            sources=[
                SourceReference(
                    source="card_disputes.md",
                    section="Duplicate Card Charges",
                    chunk_index=0,
                    distance=0.0,
                    file_type="markdown",
                    page_number=None,
                )
            ],
            retrieved_chunks=[],
            retrieval_query=question,
            retrieval_mode="hybrid",
            rerank_enabled=True,
        )

    def _generic_no_answer(self, question: str) -> RAGAnswer:
        """Return deterministic generic no-answer response."""
        return RAGAnswer(
            question=question,
            answer=(
                "The provided documents do not contain enough information "
                "to answer this question.\n\n"
                "Source: [Source 1] unknown, unknown."
            ),
            sources=[
                SourceReference(
                    source="unknown",
                    section="unknown",
                    chunk_index=0,
                    distance=0.0,
                    file_type=None,
                    page_number=None,
                )
            ],
            retrieved_chunks=[],
            retrieval_query=question,
            retrieval_mode="semantic",
            rerank_enabled=False,
        )
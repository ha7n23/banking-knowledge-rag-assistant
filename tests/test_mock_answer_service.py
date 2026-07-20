from banking_rag.services.mock_answer_service import MockAnswerService


def test_mock_answer_service_returns_qr_dispute_answer() -> None:
    service = MockAnswerService()

    result = service.answer(
        question=(
            "What should happen if my QR payment was deducted but "
            "the merchant did not receive it?"
        )
    )

    assert "may raise a dispute" in result.answer
    assert result.sources[0].source == "digital_payments.md"
    assert result.sources[0].section == "QR Payment Disputes"
    assert "[Source 1]" in result.answer


def test_mock_answer_service_returns_safe_no_answer_for_refund_timeline() -> None:
    service = MockAnswerService()

    result = service.answer(
        question="What is the exact refund timeline for a failed QR payment?"
    )

    assert "do not contain enough information" in result.answer
    assert "3 days" not in result.answer
    assert "24 hours" not in result.answer
    assert result.sources[0].source == "digital_payments.md"
    assert "[Source 1]" in result.answer


def test_mock_answer_service_returns_password_recovery_answer() -> None:
    service = MockAnswerService()

    result = service.answer(
        question="I forgot my mobile banking password. How can I get back in?"
    )

    assert "forgot password option" in result.answer
    assert "registered mobile number" in result.answer
    assert result.sources[0].source == "mobile_app_access.md"
    assert "[Source 1]" in result.answer


def test_mock_answer_service_returns_duplicate_card_charge_answer() -> None:
    service = MockAnswerService()

    result = service.answer(
        question="My debit card payment was charged twice at the same shop."
    )

    assert "duplicate card transactions" in result.answer
    assert "settlement information" in result.answer
    assert result.sources[0].source == "card_disputes.md"
    assert "[Source 1]" in result.answer
from banking_rag.retrieval.query_rewriter import rewrite_query


def test_rewrite_query_for_messy_qr_payment_issue() -> None:
    result = rewrite_query("money gone shop says no")

    assert result.was_rewritten is True
    assert "QR payment deducted" in result.rewritten_query
    assert "merchant" in result.rewritten_query


def test_rewrite_query_for_mobile_password_issue() -> None:
    result = rewrite_query("app pass forgot")

    assert result.was_rewritten is True
    assert "mobile banking password recovery" in result.rewritten_query


def test_rewrite_query_for_duplicate_card_charge() -> None:
    result = rewrite_query("my debit card was charged twice")

    assert result.was_rewritten is True
    assert "duplicate debit card charge" in result.rewritten_query


def test_rewrite_query_keeps_unclear_query_unchanged() -> None:
    result = rewrite_query("what support options are available")

    assert result.was_rewritten is False
    assert result.rewritten_query == "what support options are available"


def test_rewrite_query_strips_extra_whitespace() -> None:
    result = rewrite_query("   what support options are available   ")

    assert result.was_rewritten is False
    assert result.rewritten_query == "what support options are available"
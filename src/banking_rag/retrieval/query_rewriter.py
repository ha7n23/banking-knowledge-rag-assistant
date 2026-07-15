from banking_rag.core.schemas import QueryRewriteResult


def rewrite_query(query: str) -> QueryRewriteResult:
    """Conservatively rewrite messy user queries for better retrieval.

    The rewriter only changes the query when the intent is obvious.
    If the query is unclear, it returns the original query unchanged.
    """
    cleaned_query = " ".join(query.strip().split())
    text = cleaned_query.lower()

    if not cleaned_query:
        return QueryRewriteResult(
            original_query=query,
            rewritten_query=cleaned_query,
            was_rewritten=False,
            reason="Empty query.",
        )

    if _looks_like_qr_merchant_not_received(text):
        return QueryRewriteResult(
            original_query=query,
            rewritten_query=(
                "QR payment deducted from customer account but merchant "
                "did not receive payment confirmation"
            ),
            was_rewritten=True,
            reason="Detected likely QR payment deducted but merchant not received issue.",
        )

    if _looks_like_mobile_password_issue(text):
        return QueryRewriteResult(
            original_query=query,
            rewritten_query=(
                "mobile banking password recovery forgot password registered "
                "mobile number verification"
            ),
            was_rewritten=True,
            reason="Detected likely mobile app password recovery issue.",
        )

    if _looks_like_duplicate_card_charge(text):
        return QueryRewriteResult(
            original_query=query,
            rewritten_query=(
                "duplicate debit card charge same merchant payment charged twice"
            ),
            was_rewritten=True,
            reason="Detected likely duplicate card charge issue.",
        )

    return QueryRewriteResult(
        original_query=query,
        rewritten_query=cleaned_query,
        was_rewritten=False,
        reason="No confident rewrite rule matched.",
    )


def _looks_like_qr_merchant_not_received(text: str) -> bool:
    """Detect likely QR or merchant-not-received payment issues."""
    qr_terms = [
        "qr",
        "raast",
        "merchant",
        "shop",
        "seller",
    ]

    deducted_terms = [
        "deducted",
        "debited",
        "money gone",
        "amount gone",
        "payment gone",
        "account cut",
    ]

    not_received_terms = [
        "did not receive",
        "didn't receive",
        "not received",
        "says no",
        "saying no",
        "no confirmation",
    ]

    return (
        _contains_any(text, qr_terms)
        and _contains_any(text, deducted_terms)
        and _contains_any(text, not_received_terms)
    )


def _looks_like_mobile_password_issue(text: str) -> bool:
    """Detect likely mobile banking password or login recovery issues."""
    access_terms = [
        "password",
        "pass",
        "login",
        "log in",
        "signin",
        "sign in",
    ]

    problem_terms = [
        "forgot",
        "forget",
        "reset",
        "recover",
        "can't",
        "cannot",
        "unable",
        "locked",
    ]

    mobile_terms = [
        "app",
        "mobile",
        "mobile banking",
    ]

    return (
        _contains_any(text, access_terms)
        and _contains_any(text, problem_terms)
        and _contains_any(text, mobile_terms)
    )


def _looks_like_duplicate_card_charge(text: str) -> bool:
    """Detect likely duplicate card charge issues."""
    card_terms = [
        "card",
        "debit card",
    ]

    duplicate_terms = [
        "charged twice",
        "charge twice",
        "double charged",
        "duplicate charge",
        "same payment twice",
        "twice",
    ]

    return (
        _contains_any(text, card_terms)
        and _contains_any(text, duplicate_terms)
    )


def _contains_any(text: str, phrases: list[str]) -> bool:
    """Return True if any phrase appears in the text."""
    return any(phrase in text for phrase in phrases)
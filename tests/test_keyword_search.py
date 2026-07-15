from banking_rag.retrieval.keyword_search import keyword_score, tokenize


def test_tokenize_keeps_hyphenated_codes() -> None:
    tokens = tokenize("What does RAAST-P2M-042 mean?")

    assert "raast-p2m-042" in tokens


def test_keyword_score_rewards_exact_code_match() -> None:
    query = "What does RAAST-P2M-042 mean?"
    text = (
        "The internal sample reference code RAAST-P2M-042 refers to QR "
        "payments where the customer was debited but the merchant did not "
        "receive confirmation."
    )

    score = keyword_score(query, text)

    assert score > 0


def test_keyword_score_returns_zero_when_no_terms_match() -> None:
    score = keyword_score(
        query="mobile password reset",
        text="Duplicate card charges can be reported.",
    )

    assert score == 0
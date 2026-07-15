import re
from collections import Counter


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9\-]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "where",
    "with",
}


def tokenize(text: str) -> list[str]:
    """Tokenize text for simple keyword scoring."""
    tokens = TOKEN_PATTERN.findall(text.lower())

    return [
        token
        for token in tokens
        if len(token) > 1 and token not in STOPWORDS
    ]


def keyword_score(query: str, text: str) -> float:
    """Score how well text matches query keywords."""
    query_tokens = tokenize(query)

    if not query_tokens:
        return 0.0

    unique_query_tokens = set(query_tokens)
    text_tokens = tokenize(text)
    text_counts = Counter(text_tokens)
    text_lower = text.lower()

    score = 0.0

    for token in unique_query_tokens:
        if token in text_counts:
            score += 1.0

        if "-" in token and token in text_lower:
            score += 3.0

    if query.strip().lower() in text_lower:
        score += 2.0

    return score / len(unique_query_tokens)
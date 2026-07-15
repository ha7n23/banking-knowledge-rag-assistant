from banking_rag.core.schemas import MetadataValue


def infer_metadata_filter(query: str) -> dict[str, MetadataValue] | None:
    """Infer a safe metadata filter from a user query.

    The filter is intentionally conservative. If the query does not clearly
    point to one product/channel, return None so retrieval searches all chunks.
    """
    text = query.lower()

    if any(
        phrase in text
        for phrase in [
            "password",
            "login",
            "mobile app",
            "registered mobile",
            "otp",
        ]
    ):
        return {
            "product": "mobile_app",
        }

    if any(
        phrase in text
        for phrase in [
            "card",
            "debit card",
            "charged twice",
            "duplicate charge",
            "lost card",
            "stolen card",
        ]
    ):
        return {
            "product": "cards",
        }

    if any(
        phrase in text
        for phrase in [
            "qr",
            "raast",
            "merchant did not receive",
            "merchant didn't receive",
            "payment deducted",
            "deducted but merchant",
        ]
    ):
        return {
            "product": "digital_payments",
        }

    return None
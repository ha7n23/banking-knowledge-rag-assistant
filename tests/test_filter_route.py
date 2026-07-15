from banking_rag.retrieval.filter_router import infer_metadata_filter


def test_infer_metadata_filter_for_mobile_app_query() -> None:
    metadata_filter = infer_metadata_filter(
        "I forgot my mobile banking password."
    )

    assert metadata_filter == {"product": "mobile_app"}


def test_infer_metadata_filter_for_card_query() -> None:
    metadata_filter = infer_metadata_filter(
        "My debit card was charged twice."
    )

    assert metadata_filter == {"product": "cards"}


def test_infer_metadata_filter_for_qr_query() -> None:
    metadata_filter = infer_metadata_filter(
        "My QR payment was deducted but the merchant did not receive it."
    )

    assert metadata_filter == {"product": "digital_payments"}


def test_infer_metadata_filter_returns_none_for_unclear_query() -> None:
    metadata_filter = infer_metadata_filter(
        "What support options are available?"
    )

    assert metadata_filter is None
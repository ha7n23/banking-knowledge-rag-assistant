from banking_rag.core.schemas import RetrievedChunk
from banking_rag.generation.prompt_builder import (
    build_context_block,
    build_grounded_prompt,
)


def test_build_context_block_includes_source_metadata() -> None:
    chunks = [
        RetrievedChunk(
            text="Customers may raise a QR payment dispute.",
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            distance=0.42,
            metadata={"file_type": "markdown"},
        )
    ]

    context = build_context_block(chunks)

    assert "[Source 1]" in context
    assert "digital_payments.md" in context
    assert "QR Payment Disputes" in context
    assert "Customers may raise a QR payment dispute." in context


def test_build_grounded_prompt_includes_grounding_rules() -> None:
    chunks = [
        RetrievedChunk(
            text="Customers may raise a QR payment dispute.",
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            distance=0.42,
            metadata={},
        )
    ]

    prompt = build_grounded_prompt(
        question="What should happen if a QR payment fails?",
        retrieved_chunks=chunks,
    )

    assert "Use only the provided context" in prompt
    assert "Do not invent timelines" in prompt
    assert "provided documents do not contain enough information" in prompt
    assert "What should happen if a QR payment fails?" in prompt
from banking_rag.core.schemas import RetrievedChunk
from banking_rag.services.rag_service import BankingRAGService


class FakeRetriever:
    """Fake retriever for testing the RAG service."""

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                text=(
                    "Customers who forget their mobile banking password should "
                    "use the forgot password option in the mobile app."
                ),
                source="mobile_app_access.md",
                section="Password Recovery",
                chunk_index=0,
                distance=0.25,
                metadata={"file_type": "markdown"},
            )
        ]


class FakeLLMClient:
    """Fake LLM client for testing without live API calls."""

    def generate(self, prompt: str) -> str:
        assert "Use only the provided context" in prompt
        assert "mobile_app_access.md" in prompt
        return (
            "Customers should use the forgot password option in the mobile app.\n\n"
            "Source: [Source 1] mobile_app_access.md, Password Recovery"
        )


def test_rag_service_returns_grounded_answer() -> None:
    service = BankingRAGService(
        retriever=FakeRetriever(),
        llm_client=FakeLLMClient(),
    )

    result = service.answer("I forgot my password.")

    assert result.question == "I forgot my password."
    assert "forgot password option" in result.answer
    assert len(result.sources) == 1
    assert result.sources[0].source == "mobile_app_access.md"
    assert result.sources[0].section == "Password Recovery"
    assert len(result.retrieved_chunks) == 1
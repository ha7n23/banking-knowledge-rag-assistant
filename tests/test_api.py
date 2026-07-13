from fastapi.testclient import TestClient

from banking_rag.api.app import app
from banking_rag.api.dependencies import get_rag_service, get_retriever
from banking_rag.core.schemas import (
    RAGAnswer,
    RetrievedChunk,
    SourceReference,
)


class FakeRetriever:
    """Fake retriever for API tests."""

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                text="Customers may raise a QR payment dispute.",
                source="digital_payments.md",
                section="QR Payment Disputes",
                chunk_index=0,
                distance=0.42,
                metadata={"file_type": "markdown"},
            )
        ]


class FakeRAGService:
    """Fake RAG service for API tests."""

    def answer(self, question: str, top_k: int | None = None) -> RAGAnswer:
        chunk = RetrievedChunk(
            text="Customers may raise a QR payment dispute.",
            source="digital_payments.md",
            section="QR Payment Disputes",
            chunk_index=0,
            distance=0.42,
            metadata={"file_type": "markdown"},
        )

        return RAGAnswer(
            question=question,
            answer=(
                "The provided documents do not contain enough information "
                "to specify an exact refund timeline."
            ),
            sources=[
                SourceReference(
                    source="digital_payments.md",
                    section="QR Payment Disputes",
                    chunk_index=0,
                    distance=0.42,
                )
            ],
            retrieved_chunks=[chunk],
        )


def override_retriever() -> FakeRetriever:
    """Return fake retriever dependency."""
    return FakeRetriever()


def override_rag_service() -> FakeRAGService:
    """Return fake RAG service dependency."""
    return FakeRAGService()


client = TestClient(app)


def setup_module() -> None:
    """Override API dependencies for tests."""
    app.dependency_overrides[get_retriever] = override_retriever
    app.dependency_overrides[get_rag_service] = override_rag_service


def teardown_module() -> None:
    """Clear dependency overrides after tests."""
    app.dependency_overrides.clear()


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "app_name" in data
    assert "environment" in data


def test_retrieve_endpoint_returns_chunks() -> None:
    response = client.post(
        "/retrieve",
        json={
            "query": "What should happen if my QR payment failed?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["query"] == "What should happen if my QR payment failed?"
    assert len(data["chunks"]) == 1
    assert data["chunks"][0]["source"] == "digital_payments.md"
    assert data["chunks"][0]["section"] == "QR Payment Disputes"


def test_retrieve_endpoint_rejects_empty_query() -> None:
    response = client.post(
        "/retrieve",
        json={
            "query": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_answer_endpoint_returns_grounded_answer() -> None:
    response = client.post(
        "/answer",
        json={
            "query": "What is the exact refund timeline?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["question"] == "What is the exact refund timeline?"
    assert "do not contain enough information" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source"] == "digital_payments.md"
    assert len(data["retrieved_chunks"]) == 1


def test_answer_endpoint_rejects_empty_query() -> None:
    response = client.post(
        "/answer",
        json={
            "query": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422
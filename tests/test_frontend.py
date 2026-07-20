from fastapi.testclient import TestClient

from banking_rag.api.app import app


client = TestClient(app)


def test_frontend_homepage_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Banking Knowledge RAG Assistant" in response.text
    assert "Ask a question" in response.text
    assert "/static/app.js" in response.text
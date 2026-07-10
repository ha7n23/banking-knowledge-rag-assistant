from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Wrapper around a local Sentence Transformers embedding model."""

    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for multiple texts."""
        if not texts:
            return []

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Create an embedding for a single user query."""
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
from typing import Any


class EmbeddingModel:
    """Wrapper around a local Sentence Transformers embedding model.

    The model is loaded lazily so importing this module does not immediately
    import torch/sentence-transformers. This keeps unit tests lightweight.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any | None = None

    @property
    def model(self) -> Any:
        """Load the embedding model only when it is actually needed."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)

        return self._model

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
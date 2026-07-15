from typing import Any, Protocol

from banking_rag.core.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    TOP_K,
)
from banking_rag.core.exceptions import RetrievalError
from banking_rag.core.schemas import MetadataValue, RetrievedChunk
from banking_rag.retrieval.embedding_model import EmbeddingModel
from banking_rag.retrieval.vector_store import ChromaVectorStore


class QueryEmbedder(Protocol):
    """Protocol for any object that can embed a user query."""

    def embed_query(self, query: str) -> list[float]:
        """Create an embedding for a query."""
        ...


class KnowledgeRetriever:
    """Retrieves relevant chunks from the indexed banking knowledge base."""

    def __init__(
        self,
        embedding_model: QueryEmbedder | None = None,
        vector_store: ChromaVectorStore | None = None,
        default_top_k: int = TOP_K,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel(
            EMBEDDING_MODEL_NAME
        )
        self.vector_store = vector_store or ChromaVectorStore(
            persist_dir=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
        )
        self.default_top_k = default_top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        metadata_filter: dict[str, MetadataValue] | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a user query."""
        cleaned_query = query.strip()

        if not cleaned_query:
            raise RetrievalError("Query cannot be empty.")

        if self.vector_store.count() == 0:
            raise RetrievalError(
                "The vector store is empty. Run the indexer before querying."
            )

        query_embedding = self.embedding_model.embed_query(cleaned_query)

        results = self.vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k or self.default_top_k,
            metadata_filter=metadata_filter,
        )

        return self._parse_results(results)

    def _parse_results(self, results: dict[str, Any]) -> list[RetrievedChunk]:
        """Convert raw Chroma results into RetrievedChunk objects."""
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks: list[RetrievedChunk] = []

        for document, metadata, distance in zip(documents, metadatas, distances):
            if metadata is None:
                metadata = {}

            source = str(metadata.get("source", "unknown"))
            section = str(metadata.get("section", "Unknown"))

            raw_chunk_index = metadata.get("chunk_index", 0)
            chunk_index = int(raw_chunk_index)

            safe_metadata: dict[str, MetadataValue] = {
                key: value
                for key, value in metadata.items()
                if isinstance(value, str | int | float | bool)
            }

            retrieved_chunks.append(
                RetrievedChunk(
                    text=str(document),
                    source=source,
                    section=section,
                    chunk_index=chunk_index,
                    distance=float(distance),
                    metadata=safe_metadata,
                )
            )

        return retrieved_chunks
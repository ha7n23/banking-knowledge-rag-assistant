from typing import Any

from banking_rag.core.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    TOP_K,
)
from banking_rag.core.exceptions import RetrievalError
from banking_rag.core.schemas import (
    HybridRetrievedChunk,
    MetadataValue,
    RetrievedChunk,
)
from banking_rag.retrieval.embedding_model import EmbeddingModel
from banking_rag.retrieval.keyword_search import keyword_score
from banking_rag.retrieval.retriever import KnowledgeRetriever, QueryEmbedder
from banking_rag.retrieval.vector_store import ChromaVectorStore


class HybridRetriever:
    """Combines semantic retrieval with simple keyword scoring."""

    def __init__(
        self,
        embedding_model: QueryEmbedder | None = None,
        vector_store: ChromaVectorStore | None = None,
        default_top_k: int = TOP_K,
        semantic_candidate_k: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel(
            EMBEDDING_MODEL_NAME
        )
        self.vector_store = vector_store or ChromaVectorStore(
            persist_dir=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
        )
        self.default_top_k = default_top_k
        self.semantic_candidate_k = semantic_candidate_k
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

        self.semantic_retriever = KnowledgeRetriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            default_top_k=default_top_k,
        )

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        metadata_filter: dict[str, MetadataValue] | None = None,
    ) -> list[HybridRetrievedChunk]:
        """Retrieve chunks using a hybrid semantic + keyword score."""
        cleaned_query = query.strip()

        if not cleaned_query:
            raise RetrievalError("Query cannot be empty.")

        if self.vector_store.count() == 0:
            raise RetrievalError(
                "The vector store is empty. Run the indexer before querying."
            )

        final_top_k = top_k or self.default_top_k
        semantic_top_k = min(
            max(final_top_k * 3, self.semantic_candidate_k),
            self.vector_store.count(),
        )

        semantic_chunks = self.semantic_retriever.retrieve(
            query=cleaned_query,
            top_k=semantic_top_k,
            metadata_filter=metadata_filter,
        )

        all_chunks = self._load_all_chunks(metadata_filter=metadata_filter)

        return self._combine_results(
            query=cleaned_query,
            semantic_chunks=semantic_chunks,
            all_chunks=all_chunks,
            top_k=final_top_k,
        )

    def _load_all_chunks(
        self,
        metadata_filter: dict[str, MetadataValue] | None,
    ) -> list[RetrievedChunk]:
        """Load all chunks from Chroma for keyword scoring."""
        results = self.vector_store.get_all(metadata_filter=metadata_filter)

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        chunks: list[RetrievedChunk] = []

        for document, metadata in zip(documents, metadatas):
            if metadata is None:
                metadata = {}

            source = str(metadata.get("source", "unknown"))
            section = str(metadata.get("section", "Unknown"))
            chunk_index = int(metadata.get("chunk_index", 0))

            safe_metadata: dict[str, MetadataValue] = {
                key: value
                for key, value in metadata.items()
                if isinstance(value, str | int | float | bool)
            }

            chunks.append(
                RetrievedChunk(
                    text=str(document),
                    source=source,
                    section=section,
                    chunk_index=chunk_index,
                    distance=float("inf"),
                    metadata=safe_metadata,
                )
            )

        return chunks

    def _combine_results(
        self,
        query: str,
        semantic_chunks: list[RetrievedChunk],
        all_chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[HybridRetrievedChunk]:
        """Combine semantic rank and keyword score into one ranking."""
        semantic_rank_by_key = {
            self._chunk_key(chunk): rank
            for rank, chunk in enumerate(semantic_chunks, start=1)
        }

        semantic_chunk_by_key = {
            self._chunk_key(chunk): chunk
            for chunk in semantic_chunks
        }

        keyword_scores = {
            self._chunk_key(chunk): keyword_score(query, chunk.text)
            for chunk in all_chunks
        }

        max_keyword_score = max(keyword_scores.values(), default=0.0)

        candidate_keys = set(semantic_rank_by_key)

        candidate_keys.update(
            key for key, score in keyword_scores.items() if score > 0
        )

        all_chunk_by_key = {
            self._chunk_key(chunk): chunk
            for chunk in all_chunks
        }

        hybrid_chunks: list[HybridRetrievedChunk] = []

        for key in candidate_keys:
            base_chunk = semantic_chunk_by_key.get(key) or all_chunk_by_key[key]

            semantic_rank = semantic_rank_by_key.get(key)
            semantic_score = 0.0

            if semantic_rank is not None:
                semantic_score = 1.0 / semantic_rank

            raw_keyword_score = keyword_scores.get(key, 0.0)
            normalized_keyword_score = 0.0

            if max_keyword_score > 0:
                normalized_keyword_score = raw_keyword_score / max_keyword_score

            hybrid_score = (
                self.semantic_weight * semantic_score
                + self.keyword_weight * normalized_keyword_score
            )

            hybrid_chunks.append(
                HybridRetrievedChunk(
                    text=base_chunk.text,
                    source=base_chunk.source,
                    section=base_chunk.section,
                    chunk_index=base_chunk.chunk_index,
                    distance=base_chunk.distance,
                    metadata=base_chunk.metadata,
                    semantic_rank=semantic_rank,
                    keyword_score=raw_keyword_score,
                    hybrid_score=hybrid_score,
                )
            )

        return sorted(
            hybrid_chunks,
            key=lambda chunk: chunk.hybrid_score,
            reverse=True,
        )[:top_k]

    def _chunk_key(self, chunk: RetrievedChunk) -> tuple[str, str, int]:
        """Build a stable key for de-duplicating chunks."""
        return (
            chunk.source,
            chunk.section,
            chunk.chunk_index,
        )
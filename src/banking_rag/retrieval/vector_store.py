from pathlib import Path
from typing import Any, cast

import chromadb

from banking_rag.core.schemas import DocumentChunk


class ChromaVectorStore:
    """Chroma-backed vector store for banking document chunks."""

    def __init__(self, persist_dir: Path, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset_collection(self) -> None:
        """Delete and recreate the collection for a clean re-index."""
        collection_name = self.collection.name

        try:
            self.client.delete_collection(collection_name)
        except ValueError:
            pass

        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: Any,
    ) -> None:
        """Add chunks, embeddings, and metadata to the Chroma collection."""
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        self.collection.add(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    "source": chunk.source,
                    "section": chunk.section,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata,
                }
                for chunk in chunks
            ],
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int,
        metadata_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Retrieve the nearest chunks for a query embedding."""
        query_kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }

        if metadata_filter:
            query_kwargs["where"] = metadata_filter

        return cast(dict[str, Any], self.collection.query(**query_kwargs))

    def count(self) -> int:
        """Return the number of records in the collection."""
        return self.collection.count()
    
    def get_all(
        self,
        metadata_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return all stored chunks, optionally restricted by metadata."""
        get_kwargs: dict[str, Any] = {
            "include": ["documents", "metadatas"],
        }

        if metadata_filter:
            get_kwargs["where"] = metadata_filter

        return cast(dict[str, Any], self.collection.get(**get_kwargs))
from typing import Protocol

from banking_rag.core.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    RAW_DOCS_DIR,
)
from banking_rag.core.schemas import DocumentChunk
from banking_rag.ingestion.chunker import chunk_documents
from banking_rag.ingestion.document_loader import load_documents
from banking_rag.retrieval.embedding_model import EmbeddingModel
from banking_rag.retrieval.vector_store import ChromaVectorStore


class TextEmbedder(Protocol):
    """Protocol for embedding document chunks."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for multiple texts."""
        ...


class KnowledgeBaseIndexer:
    """Builds the searchable Chroma knowledge base from raw documents."""

    def __init__(
        self,
        embedding_model: TextEmbedder | None = None,
        vector_store: ChromaVectorStore | None = None,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store or ChromaVectorStore(
            persist_dir=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
        )

    def _get_embedding_model(self) -> TextEmbedder:
        """Create the real embedding model only when indexing is run."""
        if self.embedding_model is None:
            self.embedding_model = EmbeddingModel(EMBEDDING_MODEL_NAME)

        return self.embedding_model

    def build_chunks(self) -> list[DocumentChunk]:
        """Load raw documents and convert them into chunks."""
        documents = load_documents(RAW_DOCS_DIR)

        if not documents:
            raise ValueError(f"No markdown documents found in {RAW_DOCS_DIR}")

        chunks = chunk_documents(
            documents=documents,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        if not chunks:
            raise ValueError("No chunks were created from the documents.")

        return chunks

    def index(self, reset: bool = True) -> int:
        """
        Index raw documents into Chroma.

        Returns the number of chunks indexed.
        """
        chunks = self.build_chunks()

        embedding_model = self._get_embedding_model()
        embeddings = embedding_model.embed_texts(
            [chunk.text for chunk in chunks]
        )

        if reset:
            self.vector_store.reset_collection()

        self.vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        return len(chunks)
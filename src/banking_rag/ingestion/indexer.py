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
from banking_rag.ingestion.document_loader import load_markdown_documents
from banking_rag.retrieval.embedding_model import EmbeddingModel
from banking_rag.retrieval.vector_store import ChromaVectorStore


class KnowledgeBaseIndexer:
    """Builds the searchable Chroma knowledge base from raw documents."""

    def __init__(self) -> None:
        self.embedding_model = EmbeddingModel(EMBEDDING_MODEL_NAME)
        self.vector_store = ChromaVectorStore(
            persist_dir=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
        )

    def build_chunks(self) -> list[DocumentChunk]:
        """Load raw documents and convert them into chunks."""
        documents = load_markdown_documents(RAW_DOCS_DIR)

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

        embeddings = self.embedding_model.embed_texts(
            [chunk.text for chunk in chunks]
        )

        if reset:
            self.vector_store.reset_collection()

        self.vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        return len(chunks)
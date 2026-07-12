class BankingRAGError(Exception):
    """Base exception for the Banking RAG Assistant."""


class DocumentLoadingError(BankingRAGError):
    """Raised when documents cannot be loaded."""


class ChunkingError(BankingRAGError):
    """Raised when documents cannot be chunked properly."""

class RetrievalError(BankingRAGError):
    """Raised when retrieval fails."""

class GenerationError(BankingRAGError):
    """Raised when answer generation fails."""
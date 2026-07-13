from banking_rag.retrieval.retriever import KnowledgeRetriever
from banking_rag.services.rag_service import BankingRAGService


def get_retriever() -> KnowledgeRetriever:
    """Create the default retriever dependency."""
    return KnowledgeRetriever()


def get_rag_service() -> BankingRAGService:
    """Create the default RAG service dependency."""
    return BankingRAGService()
from banking_rag.core.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    TOP_K,
)
from banking_rag.core.schemas import (
    MetadataValue,
    RetrievalMode,
    RetrievalPipelineResult,
    RetrievedChunk,
)
from banking_rag.retrieval.embedding_model import EmbeddingModel
from banking_rag.retrieval.filter_router import infer_metadata_filter
from banking_rag.retrieval.hybrid_retriever import HybridRetriever
from banking_rag.retrieval.query_rewriter import rewrite_query
from banking_rag.retrieval.reranker import SimpleReranker
from banking_rag.retrieval.retriever import KnowledgeRetriever, QueryEmbedder
from banking_rag.retrieval.vector_store import ChromaVectorStore


class RetrievalPipeline:
    """Reusable retrieval pipeline for advanced RAG.

    The pipeline can optionally apply:

    - conservative query rewriting
    - conservative metadata filter inference
    - semantic or hybrid retrieval
    - lightweight reranking
    """

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
        self.reranker = SimpleReranker()

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        retrieval_mode: RetrievalMode = "semantic",
        metadata_filter: dict[str, MetadataValue] | None = None,
        auto_filter: bool = False,
        rewrite_query_enabled: bool = False,
        rerank: bool = False,
        candidate_k: int = 8,
    ) -> RetrievalPipelineResult:
        """Run the advanced retrieval pipeline."""
        final_top_k = top_k or self.default_top_k

        retrieval_query = query
        rewrite_result = None

        if rewrite_query_enabled:
            rewrite_result = rewrite_query(query)
            retrieval_query = rewrite_result.rewritten_query

        final_metadata_filter = metadata_filter

        if final_metadata_filter is None and auto_filter:
            final_metadata_filter = infer_metadata_filter(retrieval_query)

        retriever = self._build_retriever(retrieval_mode=retrieval_mode)

        retrieval_top_k = final_top_k

        if rerank:
            retrieval_top_k = max(final_top_k, candidate_k)

        retrieved_chunks = retriever.retrieve(
            query=retrieval_query,
            top_k=retrieval_top_k,
            metadata_filter=final_metadata_filter,
        )

        final_chunks: list[RetrievedChunk] = [
            chunk for chunk in retrieved_chunks
        ]

        if rerank:
            reranked_chunks = self.reranker.rerank(
                query=retrieval_query,
                chunks=final_chunks,
                top_k=final_top_k,
            )
            final_chunks = [chunk for chunk in reranked_chunks]

        return RetrievalPipelineResult(
            original_query=query,
            retrieval_query=retrieval_query,
            rewrite_result=rewrite_result,
            metadata_filter=final_metadata_filter,
            retrieval_mode=retrieval_mode,
            rerank_enabled=rerank,
            retrieved_chunks=final_chunks,
        )

    def _build_retriever(
        self,
        retrieval_mode: RetrievalMode,
    ) -> KnowledgeRetriever | HybridRetriever:
        """Build the requested retriever."""
        if retrieval_mode == "hybrid":
            return HybridRetriever(
                embedding_model=self.embedding_model,
                vector_store=self.vector_store,
                default_top_k=self.default_top_k,
            )

        return KnowledgeRetriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            default_top_k=self.default_top_k,
        )
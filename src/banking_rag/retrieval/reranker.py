from banking_rag.core.schemas import RerankedChunk, RetrievedChunk
from banking_rag.retrieval.keyword_search import keyword_score

from collections.abc import Sequence


class SimpleReranker:
    """Lightweight reranker for retrieved chunks.

    This is not a neural reranker. It is a transparent scoring layer used to
    demonstrate the reranking stage in an advanced RAG pipeline.
    """

    def __init__(
        self,
        semantic_weight: float = 0.45,
        keyword_weight: float = 0.40,
        section_weight: float = 0.15,
    ) -> None:
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.section_weight = section_weight

    def rerank(
        self,
        query: str,
        chunks: Sequence[RetrievedChunk],
        top_k: int,
    ) -> list[RerankedChunk]:
        """Rerank retrieved chunks and return the best top-k chunks."""
        if not chunks:
            return []

        text_keyword_scores = [
            keyword_score(query=query, text=chunk.text)
            for chunk in chunks
        ]

        section_keyword_scores = [
            keyword_score(
                query=query,
                text=f"{chunk.source} {chunk.section}",
            )
            for chunk in chunks
        ]

        max_text_keyword_score = max(text_keyword_scores, default=0.0)
        max_section_keyword_score = max(section_keyword_scores, default=0.0)

        reranked_chunks: list[RerankedChunk] = []

        for original_rank, chunk in enumerate(chunks, start=1):
            semantic_score = 1.0 / original_rank

            text_keyword_raw = text_keyword_scores[original_rank - 1]
            section_keyword_raw = section_keyword_scores[original_rank - 1]

            text_keyword_normalized = self._normalize(
                value=text_keyword_raw,
                max_value=max_text_keyword_score,
            )
            section_keyword_normalized = self._normalize(
                value=section_keyword_raw,
                max_value=max_section_keyword_score,
            )

            rerank_score = (
                self.semantic_weight * semantic_score
                + self.keyword_weight * text_keyword_normalized
                + self.section_weight * section_keyword_normalized
            )

            reranked_chunks.append(
                RerankedChunk(
                    text=chunk.text,
                    source=chunk.source,
                    section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    distance=chunk.distance,
                    metadata=chunk.metadata,
                    semantic_rank=getattr(chunk, "semantic_rank", None),
                    keyword_score=getattr(chunk, "keyword_score", 0.0),
                    hybrid_score=getattr(chunk, "hybrid_score", 0.0),
                    original_rank=original_rank,
                    rerank_keyword_score=text_keyword_raw,
                    rerank_section_score=section_keyword_raw,
                    rerank_score=rerank_score,
                )
            )

        return sorted(
            reranked_chunks,
            key=lambda chunk: chunk.rerank_score,
            reverse=True,
        )[:top_k]

    def _normalize(self, value: float, max_value: float) -> float:
        """Normalize a score between 0 and 1."""
        if max_value <= 0:
            return 0.0

        return value / max_value
"""Local cross-encoder reranker.

Bi-encoder (your embedding model) encodes question and chunks SEPARATELY -> fast
but approximate. Cross-encoder reads (question, chunk) TOGETHER -> slower but more
accurate relevance scoring. Pattern: retrieve many with the bi-encoder, then
rerank the candidates with the cross-encoder and keep the best. Runs locally.
"""
from __future__ import annotations

from functools import lru_cache

from rag.config import RERANK_MODEL


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import CrossEncoder  # lazy; ~80MB on first call
    return CrossEncoder(RERANK_MODEL)


def rerank_hits(question: str, hits: list, top_k: int) -> list:
    """hits: [(doc, meta, distance), ...] from the vector store.
    Returns the top_k hits reordered by cross-encoder relevance; the 3rd tuple
    element becomes the rerank score (higher = more relevant)."""
    if not hits:
        return hits
    pairs = [(question, doc) for doc, _, _ in hits]
    scores = _model().predict(pairs)
    ranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
    return [(doc, meta, float(score)) for (doc, meta, _d), score in ranked[:top_k]]

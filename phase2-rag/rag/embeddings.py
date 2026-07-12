"""Local embeddings via sentence-transformers. Document text never leaves your machine.

Note: the FIRST call downloads the model (~90 MB) to ~/.cache. That is a model
download, not your data being sent out.
"""
from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from rag.config import EMBED_MODEL


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    # normalize_embeddings=True so cosine similarity behaves well.
    vectors = _model().encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]

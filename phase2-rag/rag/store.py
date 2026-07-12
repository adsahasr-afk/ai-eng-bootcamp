"""Thin wrapper around a local, persistent Chroma vector store."""
from __future__ import annotations

import chromadb

from rag.config import CHROMA_DIR, COLLECTION


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # cosine space matches our normalized embeddings
    return client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def query(embedding: list[float], top_k: int):
    res = get_collection().query(query_embeddings=[embedding], n_results=top_k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    return list(zip(docs, metas, dists))  # [(text, metadata, distance), ...]


def count() -> int:
    return get_collection().count()

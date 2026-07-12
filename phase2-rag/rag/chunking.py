"""Split raw text into overlapping chunks.

Strategy: fixed-size character windows with overlap.
Trade-offs (interview-relevant):
  - Smaller chunks  -> more precise retrieval, but may lose surrounding context.
  - Larger chunks   -> more context per hit, but noisier and more tokens/cost.
  - Overlap keeps a fact from being split across a chunk boundary.
More advanced options you can add later: sentence, recursive, or semantic chunking.
"""
from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[str] = []
    start, n = 0, len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap  # step back by overlap for the next window
    return chunks

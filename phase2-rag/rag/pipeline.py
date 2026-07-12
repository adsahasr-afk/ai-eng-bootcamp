"""RAG pipeline: retrieve relevant chunks -> assemble a grounded prompt -> call Claude."""
from __future__ import annotations

import os

from rag.config import ANTHROPIC_MODEL, TOP_K
from rag.embeddings import embed_query
from rag.store import query

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the answer is not in the context, say you don't know. "
    "Cite the source filename(s) you used in square brackets."
)


def build_context(hits) -> str:
    blocks = []
    for i, (doc, meta, _dist) in enumerate(hits, 1):
        src = meta.get("source", "unknown")
        blocks.append(f"[{i}] (source: {src})\n{doc}")
    return "\n\n".join(blocks)


def answer_question(question: str, top_k: int = TOP_K) -> dict:
    hits = query(embed_query(question), top_k)
    context = build_context(hits)
    sources = sorted({m.get("source", "unknown") for _, m, _ in hits})

    user_content = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )

    # Mock mode: no key yet -> show what was retrieved without paying for a call.
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {
            "answer": "[MOCK - no API key] Retrieval works; add ANTHROPIC_API_KEY "
                      "to .env for a real grounded answer.",
            "sources": sources,
            "retrieved": [d for d, _, _ in hits],
            "mock": True,
        }

    from anthropic import Anthropic

    client = Anthropic()
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    answer = "".join(b.text for b in msg.content if b.type == "text")
    return {
        "answer": answer,
        "sources": sources,
        "retrieved": [d for d, _, _ in hits],
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "mock": False,
    }

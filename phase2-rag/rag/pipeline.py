"""RAG pipeline: retrieve -> (optional rerank) -> grounded prompt -> Claude.

Now instrumented: every call emits a structured JSON log line with latency,
token usage, estimated cost, and the sources retrieved.
"""
from __future__ import annotations

import os

from rag.config import ANTHROPIC_MODEL, FETCH_K, RERANK, TOP_K
from rag.embeddings import embed_query
from rag.observability import track
from rag.store import query

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the answer is not in the context, say you don't know. "
    "Cite the source filename(s) you used in square brackets."
)


def build_context(hits) -> str:
    blocks = []
    for i, (doc, meta, _score) in enumerate(hits, 1):
        src = meta.get("source", "unknown")
        blocks.append(f"[{i}] (source: {src})\n{doc}")
    return "\n\n".join(blocks)


def answer_question(question: str, top_k: int = TOP_K, rerank: bool | None = None) -> dict:
    use_rerank = RERANK if rerank is None else rerank

    with track("rag_query", top_k=top_k, rerank=use_rerank,
               question_preview=question[:100]) as rec:
        fetch = max(FETCH_K, top_k) if use_rerank else top_k

        hits = query(embed_query(question), fetch)
        if use_rerank:
            from rag.rerank import rerank_hits
            hits = rerank_hits(question, hits, top_k)
        else:
            hits = hits[:top_k]

        context = build_context(hits)
        sources = sorted({m.get("source", "unknown") for _, m, _ in hits})
        rec["sources"] = sources
        rec["n_chunks"] = len(hits)

        user_content = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer using only the context above."
        )

        if not os.getenv("ANTHROPIC_API_KEY"):
            rec["mode"] = "mock"
            return {
                "answer": "[MOCK - no API key] Retrieval works; add ANTHROPIC_API_KEY "
                          "to .env for a real grounded answer.",
                "sources": sources,
                "retrieved": [d for d, _, _ in hits],
                "reranked": use_rerank,
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

        rec["mode"] = "live"
        rec["model"] = msg.model
        rec["input_tokens"] = msg.usage.input_tokens
        rec["output_tokens"] = msg.usage.output_tokens

        return {
            "answer": answer,
            "sources": sources,
            "retrieved": [d for d, _, _ in hits],
            "reranked": use_rerank,
            "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens,
            "mock": False,
        }

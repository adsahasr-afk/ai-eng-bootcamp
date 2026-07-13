"""From-scratch RAG metrics (RAGAS-style). Each returns (score in [0,1], detail).

Reference-free : faithfulness, answer_relevancy, context_precision
Reference-based: context_recall, answer_correctness
Plus is_abstention() for out-of-scope questions.
Embedding imports are lazy so the pure-python helpers can be tested standalone.
"""
from __future__ import annotations

import numpy as np

from evaluation.judge import judge_json


def _cos(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def faithfulness(answer: str, contexts: list[str]):
    """Fraction of the ANSWER's atomic claims that the retrieved context supports.
    Low score = hallucination (claims not grounded in what was retrieved)."""
    ctx = "\n\n".join(contexts)
    system = "You are a strict evaluator. Respond ONLY with JSON."
    user = (
        "Break the ANSWER into atomic factual claims. For each, decide if it is "
        "supported by the CONTEXT. "
        'Respond as JSON: {"claims":[{"claim":"...","supported":true}]}\n\n'
        f"CONTEXT:\n{ctx}\n\nANSWER:\n{answer}"
    )
    claims = judge_json(system, user).get("claims", [])
    if not claims:
        return 1.0, {"claims": []}
    supported = sum(1 for c in claims if c.get("supported"))
    return supported / len(claims), {"claims": claims}


def answer_relevancy(question: str, answer: str, n: int = 3):
    """Generate N questions the ANSWER would answer, then measure their embedding
    similarity to the real question. Penalizes vague or off-topic answers."""
    system = "You generate questions. Respond ONLY with JSON."
    user = (
        f"Given this ANSWER, write {n} concise questions it directly answers. "
        'Respond as JSON: {"questions":["...","..."]}\n\n'
        f"ANSWER:\n{answer}"
    )
    generated = judge_json(system, user).get("questions", [])[:n]
    if not generated:
        return 0.0, {"generated": []}
    from rag.embeddings import embed_query, embed_texts  # lazy
    q_emb = embed_query(question)
    sims = [_cos(q_emb, g) for g in embed_texts(generated)]
    return float(np.mean(sims)), {"generated": generated, "sims": sims}


def context_precision(question: str, expected_answer: str, contexts: list[str]):
    """Are retrieved chunks relevant, and are the relevant ones ranked high?
    Uses average-precision@k (RAGAS-style): rewards relevant chunks near the top."""
    system = "You are a strict evaluator. Respond ONLY with JSON."
    numbered = "\n".join(f"[{i}] {c}" for i, c in enumerate(contexts))
    user = (
        "For each numbered CONTEXT chunk, decide if it is useful for answering the "
        "QUESTION (reference answer given). "
        'Respond as JSON: {"relevant":[true,false]} in chunk order.\n\n'
        f"QUESTION: {question}\nREFERENCE ANSWER: {expected_answer}\n\nCONTEXT:\n{numbered}"
    )
    flags = [bool(x) for x in judge_json(system, user).get("relevant", [])][: len(contexts)]
    if not any(flags):
        return 0.0, {"relevant": flags}
    hits, score = 0, 0.0
    for k, rel in enumerate(flags, 1):
        if rel:
            hits += 1
            score += hits / k
    return score / hits, {"relevant": flags}


def context_recall(expected_answer: str, contexts: list[str]):
    """Fraction of the REFERENCE answer's claims that the retrieved context covers.
    Low score = retrieval missed information needed to answer."""
    ctx = "\n\n".join(contexts)
    system = "You are a strict evaluator. Respond ONLY with JSON."
    user = (
        "Break the REFERENCE ANSWER into atomic claims. For each, decide if it can "
        "be attributed to the CONTEXT. "
        'Respond as JSON: {"claims":[{"claim":"...","supported":true}]}\n\n'
        f"CONTEXT:\n{ctx}\n\nREFERENCE ANSWER:\n{expected_answer}"
    )
    claims = judge_json(system, user).get("claims", [])
    if not claims:
        return 0.0, {"claims": []}
    supported = sum(1 for c in claims if c.get("supported"))
    return supported / len(claims), {"claims": claims}


def answer_correctness(answer: str, expected_answer: str):
    """Blend of semantic similarity (local embeddings) and an LLM factual verdict."""
    from rag.embeddings import embed_query  # lazy
    sim = _cos(embed_query(answer), embed_query(expected_answer))
    system = "You are a strict evaluator. Respond ONLY with JSON."
    user = (
        "Compare the ANSWER to the REFERENCE. Is it factually correct and complete? "
        'Respond as JSON: {"verdict":"correct"} where verdict is one of '
        "correct, partially, incorrect.\n\n"
        f"REFERENCE:\n{expected_answer}\n\nANSWER:\n{answer}"
    )
    verdict = judge_json(system, user).get("verdict", "incorrect")
    v = {"correct": 1.0, "partially": 0.5, "incorrect": 0.0}.get(verdict, 0.0)
    score = 0.5 * max(0.0, sim) + 0.5 * v
    return score, {"semantic_sim": round(sim, 3), "verdict": verdict}


def is_abstention(answer: str) -> bool:
    """Heuristic: did the model decline to answer? (good for out-of-scope Qs)."""
    low = answer.lower()
    cues = [
        "don't know", "do not know", "not in the context", "no information",
        "cannot find", "isn't in", "is not in", "not provided", "unable to",
        "no mention", "does not contain", "doesn't contain",
    ]
    return any(c in low for c in cues)

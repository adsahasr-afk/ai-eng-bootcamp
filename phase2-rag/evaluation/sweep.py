"""Config sweep: run the eval across chunking / TOP_K settings and tabulate,
repeating each config so we can report mean +/- std (std = judge/generation
noise). This is how you tell a real difference from random wobble.

Usage:  python -m evaluation.sweep
Notes:
  - Stop the uvicorn server first (both touch the same Chroma store).
  - Makes MANY Claude calls. With the defaults below (~8 eval runs) that is
    a few hundred small calls -> a few cents and several minutes.
  - Edit CHUNK_CONFIGS / TOP_KS / REPEATS to spend less.
  - The index is REBUILT to your project defaults at the end. If you Ctrl+C
    mid-run, just run 'python ingest.py' to restore it.
"""
from __future__ import annotations

import os
import statistics
from datetime import date

from dotenv import load_dotenv

load_dotenv()

import chromadb  # noqa: E402

from rag.chunking import chunk_text                                        # noqa: E402
from rag.config import (CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION,  # noqa: E402
                        DATA_DIR)
from rag.embeddings import embed_texts                                     # noqa: E402
from rag.pipeline import answer_question                                   # noqa: E402
from evaluation import metrics as M                                        # noqa: E402
from evaluation.golden_set import ADVERSARIAL, GOLDEN                       # noqa: E402

# ---- what to sweep (edit freely) ----
CHUNK_CONFIGS = [(500, 80), (200, 40)]   # (chunk_size, overlap)
TOP_KS = [2, 4]
REPEATS = 2                              # runs per config; >=2 to get a std

METRIC_NAMES = [
    "faithfulness", "answer_relevancy", "context_precision",
    "context_recall", "answer_correctness",
]


def reingest(chunk_size: int, overlap: int) -> int:
    """Rebuild the main collection using a specific chunk config. Returns #chunks."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    for f in sorted(DATA_DIR.glob("*")):
        if f.suffix not in {".md", ".txt"}:
            continue
        chunks = chunk_text(f.read_text(encoding="utf-8"), chunk_size, overlap)
        if not chunks:
            continue
        col.add(
            ids=[f"{f.stem}-{i}" for i in range(len(chunks))],
            embeddings=embed_texts(chunks),
            documents=chunks,
            metadatas=[{"source": f.name, "chunk": i} for i in range(len(chunks))],
        )
    return col.count()


def evaluate_once(top_k: int) -> dict:
    """One full pass over the golden set at a given top_k. Returns metric means."""
    scores = {k: [] for k in METRIC_NAMES}
    for item in GOLDEN:
        q = item["question"]
        res = answer_question(q, top_k)
        ans, ctx = res["answer"], res["retrieved"]
        scores["faithfulness"].append(M.faithfulness(ans, ctx)[0])
        scores["answer_relevancy"].append(M.answer_relevancy(q, ans)[0])
        scores["context_precision"].append(M.context_precision(q, item["expected_answer"], ctx)[0])
        scores["context_recall"].append(M.context_recall(item["expected_answer"], ctx)[0])
        scores["answer_correctness"].append(M.answer_correctness(ans, item["expected_answer"])[0])
    out = {k: statistics.mean(v) for k, v in scores.items()}
    out["abstention"] = sum(
        M.is_abstention(answer_question(q, top_k)["answer"]) for q in ADVERSARIAL
    ) / len(ADVERSARIAL)
    return out


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Sweep needs a live key. Add ANTHROPIC_API_KEY to .env.")
        return
    n_runs = len(CHUNK_CONFIGS) * len(TOP_KS) * REPEATS
    print(f"Sweep: {len(CHUNK_CONFIGS)} chunk x {len(TOP_KS)} top_k x {REPEATS} repeats "
          f"= {n_runs} eval runs. Many Claude calls (a few cents, several minutes).")
    print("Stop the uvicorn server first. Ctrl+C to abort.\n")

    cols = METRIC_NAMES + ["abstention"]
    results = []
    for cs, ov in CHUNK_CONFIGS:
        n_chunks = reingest(cs, ov)
        print(f"[reingest] chunk_size={cs} overlap={ov} -> {n_chunks} chunks")
        for tk in TOP_KS:
            runs = [evaluate_once(tk) for _ in range(REPEATS)]
            agg = {}
            for k in cols:
                vals = [r[k] for r in runs]
                agg[k] = (statistics.mean(vals),
                          statistics.pstdev(vals) if len(vals) > 1 else 0.0)
            results.append((cs, ov, n_chunks, tk, agg))
            print(f"   top_k={tk}: " +
                  "  ".join(f"{k[:9]}={agg[k][0]:.2f}+/-{agg[k][1]:.2f}" for k in METRIC_NAMES))

    restored = reingest(CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"\n[restored] index rebuilt to defaults: chunk_size={CHUNK_SIZE} -> {restored} chunks")

    _write(results, cols)


def _write(results, cols) -> None:
    ncols = 4 + len(cols)  # chunk_size, overlap, n_chunks, top_k + metrics
    L = [f"# RAG Config Sweep ({date.today().isoformat()})\n"]
    L.append(f"Repeats per config: {REPEATS}. Cells are mean+/-std across repeats "
             "(std ~ judge/generation noise; treat differences smaller than std as not real).\n")
    L.append("| chunk_size | overlap | n_chunks | top_k | " + " | ".join(cols) + " |")
    L.append("|" + "---|" * ncols)
    for cs, ov, nc, tk, agg in results:
        cells = " | ".join(f"{agg[k][0]:.2f}+/-{agg[k][1]:.2f}" for k in cols)
        L.append(f"| {cs} | {ov} | {nc} | {tk} | {cells} |")
    with open("sweep_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("Wrote sweep_results.md")


if __name__ == "__main__":
    main()

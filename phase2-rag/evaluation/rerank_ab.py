"""A/B test: measure the lift from reranking.

Runs the golden set with rerank OFF and ON, scores both with the same metrics,
and prints a side-by-side table with deltas. Repeats for variance so you can
tell a real lift from judge noise. Writes rerank_results.md.

Usage:  python -m evaluation.rerank_ab
Stop the uvicorn server first; needs a key + an ingested store.
"""
from __future__ import annotations

import os
import statistics
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from rag.config import TOP_K            # noqa: E402
from rag.pipeline import answer_question  # noqa: E402
from rag.store import count               # noqa: E402
from evaluation import metrics as M       # noqa: E402
from evaluation.golden_set import GOLDEN  # noqa: E402

REPEATS = 2
METRIC_NAMES = [
    "faithfulness", "answer_relevancy", "context_precision",
    "context_recall", "answer_correctness",
]
CONDITIONS = {"baseline": False, "reranked": True}


def eval_condition(rerank_flag: bool) -> dict:
    scores = {k: [] for k in METRIC_NAMES}
    for item in GOLDEN:
        q = item["question"]
        res = answer_question(q, TOP_K, rerank=rerank_flag)
        ans, ctx = res["answer"], res["retrieved"]
        scores["faithfulness"].append(M.faithfulness(ans, ctx)[0])
        scores["answer_relevancy"].append(M.answer_relevancy(q, ans)[0])
        scores["context_precision"].append(M.context_precision(q, item["expected_answer"], ctx)[0])
        scores["context_recall"].append(M.context_recall(item["expected_answer"], ctx)[0])
        scores["answer_correctness"].append(M.answer_correctness(ans, item["expected_answer"])[0])
    return {k: statistics.mean(v) for k, v in scores.items()}


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Needs a live key. Add ANTHROPIC_API_KEY to .env.")
        return
    if count() == 0:
        print("Vector store empty. Run 'python ingest.py' first.")
        return

    print(f"Rerank A/B over golden set, {REPEATS} repeats per condition. "
          "Stop the server first; makes many Claude calls (a few cents).\n")

    agg = {name: {k: [] for k in METRIC_NAMES} for name in CONDITIONS}
    for r in range(REPEATS):
        for name, flag in CONDITIONS.items():
            res = eval_condition(flag)
            for k in METRIC_NAMES:
                agg[name][k].append(res[k])
            print(f"  run {r+1} {name:9s}: " +
                  "  ".join(f"{k[:9]}={res[k]:.2f}" for k in METRIC_NAMES))

    means = {n: {k: statistics.mean(v) for k, v in d.items()} for n, d in agg.items()}
    stds = {n: {k: (statistics.pstdev(v) if len(v) > 1 else 0.0) for k, v in d.items()}
            for n, d in agg.items()}

    print("\n=== LIFT (reranked - baseline) ===")
    for k in METRIC_NAMES:
        delta = means["reranked"][k] - means["baseline"][k]
        noise = max(stds["reranked"][k], stds["baseline"][k])
        tag = "  (within noise)" if abs(delta) <= noise else ""
        print(f"  {k:20s} base={means['baseline'][k]:.2f}  rerank={means['reranked'][k]:.2f}  "
              f"delta={delta:+.2f}{tag}")

    _write(means, stds)


def _write(means, stds) -> None:
    L = [f"# Rerank A/B Results ({date.today().isoformat()})\n"]
    L.append(f"Repeats per condition: {REPEATS}. Delta smaller than std = within noise.\n")
    L.append("| Metric | baseline | reranked | delta |")
    L.append("|---|---|---|---|")
    for k in METRIC_NAMES:
        delta = means["reranked"][k] - means["baseline"][k]
        L.append(f"| {k} | {means['baseline'][k]:.2f} | {means['reranked'][k]:.2f} | {delta:+.2f} |")
    with open("rerank_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\nWrote rerank_results.md")


if __name__ == "__main__":
    main()

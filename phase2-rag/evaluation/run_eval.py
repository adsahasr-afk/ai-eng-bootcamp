"""Run the golden set through the RAG pipeline and score it. Writes eval_results.md.

Usage:  python -m evaluation.run_eval
Requires: an ingested store (python ingest.py) + ANTHROPIC_API_KEY in .env.

Cost note: this makes several Claude calls per question (generation + judging).
For ~7 questions that is roughly 40-50 small calls -> a few cents total.
"""
from __future__ import annotations

import os
import statistics
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, TOP_K  # noqa: E402
from rag.pipeline import answer_question                  # noqa: E402
from rag.store import count                                # noqa: E402
from evaluation import metrics as M                        # noqa: E402
from evaluation.golden_set import ADVERSARIAL, GOLDEN      # noqa: E402

METRIC_NAMES = [
    "faithfulness", "answer_relevancy", "context_precision",
    "context_recall", "answer_correctness",
]


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Eval needs a live key (judge + generation). Add ANTHROPIC_API_KEY to .env.")
        return
    if count() == 0:
        print("Vector store is empty. Run 'python ingest.py' first.")
        return

    agg = {k: [] for k in METRIC_NAMES}
    rows = []

    for item in GOLDEN:
        q = item["question"]
        res = answer_question(q, TOP_K)
        ans, ctx = res["answer"], res["retrieved"]

        scores = {
            "faithfulness": M.faithfulness(ans, ctx)[0],
            "answer_relevancy": M.answer_relevancy(q, ans)[0],
            "context_precision": M.context_precision(q, item["expected_answer"], ctx)[0],
            "context_recall": M.context_recall(item["expected_answer"], ctx)[0],
            "answer_correctness": M.answer_correctness(ans, item["expected_answer"])[0],
        }
        for k, v in scores.items():
            agg[k].append(v)
        rows.append((q, scores, res["sources"]))
        print(f"Q: {q[:58]}")
        print("   " + "  ".join(f"{k[:9]}={scores[k]:.2f}" for k in METRIC_NAMES))

    abstained = 0
    for q in ADVERSARIAL:
        res = answer_question(q, TOP_K)
        ok = M.is_abstention(res["answer"])
        abstained += int(ok)
        print(f"[adversarial] {q[:48]} -> abstained={ok}")

    means = {k: (statistics.mean(v) if v else 0.0) for k, v in agg.items()}
    abst_rate = abstained / len(ADVERSARIAL) if ADVERSARIAL else 0.0

    print("\n=== MEANS (over golden set) ===")
    for k in METRIC_NAMES:
        print(f"  {k:20s} {means[k]:.3f}")
    print(f"  {'abstention_rate':20s} {abst_rate:.3f}")

    _write_report(rows, means, abst_rate)


def _write_report(rows, means, abst_rate) -> None:
    L = []
    L.append(f"# RAG Eval Results ({date.today().isoformat()})\n")
    L.append(f"Config: CHUNK_SIZE={CHUNK_SIZE}, CHUNK_OVERLAP={CHUNK_OVERLAP}, TOP_K={TOP_K}\n")
    L.append("## Aggregate (mean over golden set)\n")
    L.append("| Metric | Score |")
    L.append("|---|---|")
    for k in METRIC_NAMES:
        L.append(f"| {k} | {means[k]:.3f} |")
    L.append(f"| abstention_rate | {abst_rate:.3f} |")
    L.append("\n## Per-question\n")
    L.append("| Question | faith | relev | ctx_prec | ctx_rec | correct |")
    L.append("|---|---|---|---|---|---|")
    for q, s, _src in rows:
        qq = q.replace("|", "/")[:58]
        L.append(
            f"| {qq} | {s['faithfulness']:.2f} | {s['answer_relevancy']:.2f} | "
            f"{s['context_precision']:.2f} | {s['context_recall']:.2f} | "
            f"{s['answer_correctness']:.2f} |"
        )
    with open("eval_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\nWrote eval_results.md")


if __name__ == "__main__":
    main()

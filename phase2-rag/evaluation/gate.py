"""Local eval gate: run the golden set and FAIL if quality drops below thresholds.

This is the PAID tier - it makes real Claude calls, so it runs on YOUR machine,
never on third-party CI runners. Your API key stays local.

Usage:  python -m evaluation.gate
Exit code: 0 = pass, 1 = fail (so it can gate a pre-push hook).

Tune THRESHOLDS from your measured baseline - set them a little below your
observed scores so normal judge noise does not cause false alarms.
"""
from __future__ import annotations

import os
import statistics
import sys

from dotenv import load_dotenv

load_dotenv()

from rag.config import TOP_K              # noqa: E402
from rag.pipeline import answer_question  # noqa: E402
from rag.store import count                # noqa: E402
from evaluation import metrics as M        # noqa: E402
from evaluation.golden_set import ADVERSARIAL, GOLDEN  # noqa: E402

THRESHOLDS = {
    "faithfulness": 0.90,
    "answer_relevancy": 0.60,
    "context_precision": 0.80,
    "context_recall": 0.90,
    "answer_correctness": 0.75,
    "abstention_rate": 0.75,
}

METRIC_NAMES = [
    "faithfulness", "answer_relevancy", "context_precision",
    "context_recall", "answer_correctness",
]


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("FAIL: ANTHROPIC_API_KEY not set (this tier needs a live key).")
        return 1
    if count() == 0:
        print("FAIL: vector store is empty - run 'python ingest.py' first.")
        return 1

    scores = {k: [] for k in METRIC_NAMES}
    for item in GOLDEN:
        q = item["question"]
        res = answer_question(q, TOP_K)
        ans, ctx = res["answer"], res["retrieved"]
        scores["faithfulness"].append(M.faithfulness(ans, ctx)[0])
        scores["answer_relevancy"].append(M.answer_relevancy(q, ans)[0])
        scores["context_precision"].append(M.context_precision(q, item["expected_answer"], ctx)[0])
        scores["context_recall"].append(M.context_recall(item["expected_answer"], ctx)[0])
        scores["answer_correctness"].append(M.answer_correctness(ans, item["expected_answer"])[0])

    results = {k: statistics.mean(v) for k, v in scores.items()}
    results["abstention_rate"] = sum(
        M.is_abstention(answer_question(q, TOP_K)["answer"]) for q in ADVERSARIAL
    ) / len(ADVERSARIAL)

    print(f"\n{'metric':22s} {'score':>7s} {'min':>7s}  result")
    print("-" * 48)
    failed = []
    for name, threshold in THRESHOLDS.items():
        score = results.get(name, 0.0)
        ok = score >= threshold
        if not ok:
            failed.append(name)
        print(f"{name:22s} {score:7.3f} {threshold:7.2f}  {'PASS' if ok else 'FAIL'}")

    if failed:
        print(f"\nGATE FAILED on: {', '.join(failed)}")
        return 1
    print("\nGATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

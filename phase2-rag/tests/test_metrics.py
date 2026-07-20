"""Metric MATH is deterministic - we stub the LLM judge and assert the formulas.
This catches scoring bugs without spending a cent."""
import evaluation.metrics as M


def test_cosine():
    assert abs(M._cos([1, 0], [1, 0]) - 1.0) < 1e-6
    assert abs(M._cos([1, 0], [0, 1]) - 0.0) < 1e-6


def test_context_precision_average_precision(monkeypatch):
    # relevant at ranks 1 and 3 -> (1/1 + 2/3) / 2 = 0.8333
    monkeypatch.setattr(M, "judge_json", lambda s, u: {"relevant": [True, False, True, False]})
    score, _ = M.context_precision("q", "exp", ["a", "b", "c", "d"])
    assert abs(score - 0.8333) < 1e-3


def test_context_precision_all_irrelevant(monkeypatch):
    monkeypatch.setattr(M, "judge_json", lambda s, u: {"relevant": [False, False]})
    score, _ = M.context_precision("q", "exp", ["a", "b"])
    assert score == 0.0


def test_faithfulness_is_supported_fraction(monkeypatch):
    monkeypatch.setattr(M, "judge_json", lambda s, u: {"claims": [
        {"claim": "x", "supported": True},
        {"claim": "y", "supported": False},
    ]})
    score, _ = M.faithfulness("ans", ["ctx"])
    assert abs(score - 0.5) < 1e-9


def test_context_recall(monkeypatch):
    monkeypatch.setattr(M, "judge_json", lambda s, u: {"claims": [
        {"claim": "x", "supported": True},
    ]})
    score, _ = M.context_recall("ref", ["ctx"])
    assert score == 1.0


def test_abstention_detection():
    assert M.is_abstention("I don't know based on the context.")
    assert M.is_abstention("That is not provided in the documents.")
    assert not M.is_abstention("Employees get 25 days of leave.")

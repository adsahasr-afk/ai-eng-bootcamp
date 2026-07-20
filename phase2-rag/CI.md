# Continuous Evaluation - two tiers

LLM quality regressions are silent: nothing throws, the answers just get worse.
So we test two different things two different ways.

## Tier 1 - deterministic tests (free, automatic)

Runs in GitHub Actions on every push/PR. **No API key, no cost, no torch.**
Catches the failures that are actually deterministic:

- chunking logic (sizes, overlap, whitespace, edge cases)
- metric math (average-precision, supported-claim fractions, abstention)
- config sanity (overlap < chunk size, FETCH_K >= TOP_K)

Run locally the same way CI does:
```bash
cd ~/ai-eng-bootcamp/phase2-rag
pip install pytest numpy      # already covered if your venv has them
python -m pytest -q tests
```

## Tier 2 - the eval gate (paid, LOCAL ONLY)

Runs the golden set through the real pipeline and fails on regression.
This makes real Claude calls, so it stays on your machine - your API key is
never stored in GitHub Secrets or exposed to third-party runners.

```bash
cd ~/ai-eng-bootcamp/phase2-rag
source .venv/bin/activate
python -m evaluation.gate      # exit 0 = pass, 1 = regression
```

Run it before pushing any change to prompts, chunking, retrieval, or the model.

### Thresholds
Set in `evaluation/gate.py`. Keep them slightly BELOW your measured baseline so
normal LLM-judge noise does not cause false failures. Re-baseline deliberately
(with `evaluation/sweep.py`), not by quietly lowering a threshold to go green.

### Optional: gate your pushes
Only do this if you accept paying for evals on every push:
```bash
cat > .git/hooks/pre-push <<'HOOK'
#!/usr/bin/env bash
cd "$(git rev-parse --show-toplevel)/phase2-rag" || exit 0
source .venv/bin/activate 2>/dev/null
python -m evaluation.gate || { echo "eval gate failed - push aborted"; exit 1; }
HOOK
chmod +x .git/hooks/pre-push
```

## Why split this way
Putting the paid evals in CI would mean storing your Anthropic key in GitHub
Secrets and spending money on every push. Deterministic tests catch the cheap,
common breakages automatically; the expensive quality check stays deliberate and
local. That is the trade-off - and being able to explain it is the point.

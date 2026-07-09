# Phase 1 - Hello LLM (FastAPI + Anthropic)

First end-to-end AI app: an HTTP service that forwards a message to Claude and
returns the reply plus token usage.

## Two modes
- Mock mode (default, no key): /chat returns a canned reply. Build and test the
  whole loop today at zero cost.
- Live mode: add ANTHROPIC_API_KEY to .env and restart - real Claude calls kick
  in automatically. No code change needed.

## Run
```bash
cd ~/ai-eng-bootcamp/phase1-llm-foundations
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Optional now, required for live mode:
cp .env.example .env        # then edit .env and paste your key (local only)

uvicorn app.main:app --reload --port 8000
```

## Test
```bash
# health - shows "mode": "mock" until you add a key
curl http://127.0.0.1:8000/health

# chat
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain what an LLM token is in one sentence."}'
```
Interactive docs: open http://127.0.0.1:8000/docs in a browser.

## Notes
- The API key lives only in .env (gitignored). Never commit it.
- Confirm the current model string at docs.anthropic.com/en/docs/about-claude/models
  and update ANTHROPIC_MODEL in .env if needed.

## Learning checklist
- [ ] Run in mock mode, see the request/response loop work
- [ ] First successful live /chat response (after adding a key)
- [ ] Read the token counts and note the cost model
- [ ] Add a custom system prompt and see behavior change
- [ ] (Stretch) add a streaming endpoint

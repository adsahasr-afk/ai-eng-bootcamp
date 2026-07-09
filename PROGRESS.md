# Progress Tracker — AI Engineering Bootcamp

Daily log for the 8-week / 4-phase curriculum. Update it at the end of each session (2 min), then commit it with your work. Consistency > intensity.

## How to use
- Add one row to the **Daily Log** each day you work.
- Tick items in the **Phase Checklists** as you complete them.
- Keep the **Current Status** block at the top up to date.
- Commit it: `git add PROGRESS.md && git commit -m "log: <date>"`

---

## Current Status
- **Phase:** 1 — LLM Foundations & API Fluency
- **Week:** 1 of 8
- **Focus this week:** environment done → build first end-to-end LLM app
- **Current streak:** 0 days
- **Next action:** create venv + FastAPI "hello LLM" app

---

## Daily Log

| Date | Day | Hrs | Phase | What I did | Blockers / Questions | Commit |
|------|-----|-----|-------|------------|----------------------|--------|
| 2026-07-09 | 1 | 1.0 | Setup | WSL2 + Python + Git + GitHub verified, project scaffolded | — | scaffold |
|  |  |  |  |  |  |  |

---

## Phase Checklists

### Phase 1 — LLM Foundations & API Fluency (Weeks 1–2)
Goal: understand how LLMs work, use the major APIs confidently, ship a first AI app end-to-end.

- [ ] Anthropic API key working from `.env` (never committed)
- [ ] First API call (single prompt → response)
- [ ] Streaming responses
- [ ] System prompts + multi-turn messages
- [ ] Token counting / cost awareness
- [ ] FastAPI `/chat` endpoint wrapping the model
- [ ] Run app locally end-to-end
- [ ] Committed + pushed to GitHub

### Phase 2 — RAG Architecture & Evaluation (Weeks 3–4)
Goal: design, build, and systematically evaluate a production-grade RAG system.

- [ ] Document loading + chunking (compare strategies)
- [ ] Embeddings + vector store
- [ ] Retrieval + prompt assembly
- [ ] Hybrid retrieval / reranking
- [ ] Eval harness (RAGAS: faithfulness, relevancy)
- [ ] Documented eval metrics in README
- [ ] Committed + pushed

### Phase 3 — AI Agents & Orchestration (Weeks 5–6)
Goal: build autonomous agents that reason, plan, and use tools.

- [ ] ReAct loop (reason → act → observe)
- [ ] Tool calling + tool-error handling
- [ ] Loop / runaway prevention
- [ ] Multi-step task with 2+ tools
- [ ] Orchestration (LangGraph or equivalent)
- [ ] Committed + pushed

### Phase 4 — LLMOps, Observability & Production (Weeks 7–8)
Goal: package, observe, evaluate continuously, and ship.

- [ ] Dockerfile + containerized run
- [ ] Observability (Langfuse traces)
- [ ] Continuous evals in CI (prompt-regression check)
- [ ] Deployed with a **live URL**
- [ ] Architecture diagram in README
- [ ] Committed + pushed

---

## Weekly Reflection (fill in each Sunday)

**Week __**
- Wins:
- Stuck on / didn't finish:
- One thing to explain out loud (interview prep):
- Next week's #1 priority:

---

## Portfolio Must-Haves (track toward the job)
- [ ] 1 deployed project with a live URL in résumé
- [ ] README with architecture diagram (draw.io / Excalidraw)
- [ ] Eval metrics documented (e.g. faithfulness: 0.87)
- [ ] Clean git history — commit by feature, not giant dumps
- [ ] Capstone chosen and scoped

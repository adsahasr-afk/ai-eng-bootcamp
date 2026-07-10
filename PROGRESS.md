# Progress Tracker — AI Engineering Bootcamp

Daily log for the 8-week / 4-phase curriculum. Update it at the end of each session (2 min), then commit it with your work. Consistency > intensity.

## How to use

- Add one row to the **Daily Log** each day you work.
- Tick items in the **Phase Checklists** as you complete them.
- Keep the **Current Status** block at the top up to date.
- Commit it: `git add PROGRESS.md && git commit -m "log: <date>"`

---

## Current Status

## Current Status

- **Phase:** 1 COMPLETE → starting Phase 2 (RAG Architecture & Evaluation)
- **Week:** 2 of 8
- **Focus this week:** kick off RAG — document loading, chunking, embeddings, vector store
- **Current streak:** 3 days
- **Next action:** scaffold phase2-rag/ (optional carryover: streaming endpoint to close Phase 1)

---



## Daily Log


| Date       | Day | Hrs | Phase   | What I did                                                                              | Blockers / Questions                                                | Commit                 |
| ---------- | --- | --- | ------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------- |
| 2026-07-09 | 1   | 1.0 | Setup   | WSL2 + Python + Git + GitHub verified, project scaffolded                               | —                                                                   | scaffold               |
| 2026-07-09 | 1   | 1.0 | Phase 1 | Built + ran FastAPI hello-LLM app in mock mode; /health and /chat working end-to-end    | Needed python3-venv + pip installed; API key deferred (no card yet) | feat: phase1 hello-LLM |
| 2026-07-11 | 3   | 0.5 | Phase 1 | Added billing + API key, went live; /chat returns real Claude replies with token counts | Console requires workspace-scoped key (used Default)                | live api               |


---



## Phase Checklists



### Phase 1 — LLM Foundations & API Fluency (Weeks 1–2)

Goal: understand how LLMs work, use the major APIs confidently, ship a first AI app end-to-end.

- [x] Anthropic API key working from `.env` (never committed)
- [x] First API call (single prompt → response)
- [ ] Streaming responses
- [ ] System prompts + multi-turn messages
- [ ] Token counting / cost awareness
- [ ] FastAPI `/chat` endpoint wrapping the model
- [x] Run app locally end-to-end
- [x] Committed + pushed to GitHub



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
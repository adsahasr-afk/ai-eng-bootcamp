# Progress Tracker — AI Engineering Bootcamp

Daily log for the 8-week / 4-phase curriculum. Update it at the end of each session (2 min), then commit it with your work. Consistency > intensity.

## How to use

- Add one row to the **Daily Log** each day you work.
- Tick items in the **Phase Checklists** as you complete them.
- Keep the **Current Status** block at the top up to date.
- Commit it: `git add PROGRESS.md && git commit -m "log: <date>"`

---

## Current Status
- Phase: 4 IN PROGRESS - LLMOps, Observability & Production
- Week: 4 of 8
- Current streak: 7
- Done in P4: containerized RAG service (Docker), structured JSON observability
  (latency/tokens/cost/sources), two-tier continuous evaluation (free CI tests +
  local paid eval gate - all 6 metrics passing)
- Next action: architecture diagram in README; then decide on public deploy
  (needs auth + rate limiting first - endpoint proxies a paid LLM)
--



## Daily Log


| Date       | Day | Hrs | Phase   | What I did                                                                              | Blockers / Questions                                                | Commit                 |
| ---------- | --- | --- | ------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------- |
| 2026-07-09 | 1   | 1.0 | Setup   | WSL2 + Python + Git + GitHub verified, project scaffolded                               | —                                                                   | scaffold               |
| 2026-07-09 | 1   | 1.0 | Phase 1 | Built + ran FastAPI hello-LLM app in mock mode; /health and /chat working end-to-end    | Needed python3-venv + pip installed; API key deferred (no card yet) | feat: phase1 hello-LLM |
| 2026-07-10 | 3   | 0.5 | Phase 1 | Added billing + API key, went live; /chat returns real Claude replies with token counts | Console requires workspace-scoped key (used Default)                | live api               |
| 2026-07-12 | 4   | 1.0 | Phase 2 | Scaffolded from-scratch RAG pipeline: chunking, local embeddings (sentence-transformers), Chroma store, retrieval+grounded /ask, sample docs | Separate venv + .env per project (reused Phase 1 key) | feat: phase2 rag scaffold |
| 2026-07-12 | 4   | 1.5 | Phase 2 | RAG live end-to-end: ingested 7 chunks, /ask returns grounded, cited answers; understood chunking + TOP_K retrieval behavior | Noted retrieval precision + citation-faithfulness gaps (deferred, not broken) | feat: phase2 rag working |
| 2026-07-13 | 5   | 2.0 | Phase 2 | Built from-scratch eval harness (5 metrics + abstention) and config sweep w/ variance; found chunk_size the dominant lever, tuned to 500/TOP_K=2 | LLM-judge variance -> used repeats; n=7 small | feat: phase2 eval + sweep |
| 2026-07-14 | 6   | 1.5 | Phase 3 | From-scratch ReAct agent (Claude tool-use): calculator + KB-lookup reusing Phase 2 RAG; multi-tool chaining + runaway guard verified | .env doesn't hot-reload — restart to apply config | feat: phase3 react agent |
---



## Phase Checklists



### Phase 1 — LLM Foundations & API Fluency (Week 1 of 8)

Goal: understand how LLMs work, use the major APIs confidently, ship a first AI app end-to-end.

- [x] Anthropic API key working from `.env` (never committed)
- [x] First API call (single prompt → response)
- [ ] Streaming responses
- [ ] System prompts + multi-turn messages
- [x] Token counting / cost awareness
- [x] FastAPI `/chat` endpoint wrapping the model
- [x] Run app locally end-to-end
- [x] Committed + pushed to GitHub



### Phase 2 — RAG Architecture & Evaluation (Week 2 of 8)

Goal: design, build, and systematically evaluate a production-grade RAG system.

- [x] Document loading + chunking (compare strategies)
- [x] Embeddings + vector store
- [x] Retrieval + prompt assembly
- [x] Hybrid retrieval / reranking
- [x] Eval harness (RAGAS: faithfulness, relevancy)
- [x] Documented eval metrics in README
- [x] Committed + pushed



### Phase 3 — AI Agents & Orchestration (Weeks 5–6)

Goal: build autonomous agents that reason, plan, and use tools.

- [x] ReAct loop (reason → act → observe)
- [x] Tool calling + tool-error handling
- [x] Loop / runaway prevention
- [x] Multi-step task with 2+ tools
- [ ] Orchestration (LangGraph or equivalent)
- [x] Committed + pushed



### Phase 4 — LLMOps, Observability & Production (Weeks 7–8)

Goal: package, observe, evaluate continuously, and ship.

- [x] Dockerfile + containerized run
- [x] Observability (Langfuse traces)
- [x] Continuous evals in CI (prompt-regression check)
- [ ] Deployed with a **live URL**
- [x] Architecture diagram in README
- [x] Committed + pushed

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
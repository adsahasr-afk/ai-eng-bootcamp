# Phase 3 - AI Agents & Orchestration

A from-scratch ReAct agent on Claude's native tool-use API.

## Loop (reason -> act -> observe)
1. Send the question + tool schemas to Claude.
2. If Claude requests a tool, run it and feed the result back.
3. Repeat until Claude gives a final answer or MAX_ITERS is hit (runaway guard).

## Tools
- calculator            safe arithmetic (no eval/exec)
- knowledge_base_lookup queries your Phase 2 RAG service (port 8001)

## Setup
```bash
cd ~/ai-eng-bootcamp/phase3-agents
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # reuse your Anthropic key
```

## Run
The knowledge_base_lookup tool calls Phase 2, so start that first (separate tab):
```bash
# tab 1: Phase 2 RAG on 8001
cd ~/ai-eng-bootcamp/phase2-rag && source .venv/bin/activate
uvicorn app.main:app --port 8001

# tab 2: this agent on 8002
cd ~/ai-eng-bootcamp/phase3-agents && source .venv/bin/activate
uvicorn app.main:app --reload --port 8002
```

## Ask
```bash
# multi-tool: needs a KB lookup THEN arithmetic
curl -X POST http://127.0.0.1:8002/agent -H "Content-Type: application/json" \
  -d '{"question":"How many days of annual leave do employees get, and how many is that over 3 years?"}'

# calculator only
curl -X POST http://127.0.0.1:8002/agent -H "Content-Type: application/json" \
  -d '{"question":"What is (25 + 5) * 12?"}'
```
The response includes `steps` (each tool call it made), `iterations`, and how it `stopped`.

## Learning checklist
- [ ] ReAct loop runs (reason -> act -> observe)
- [ ] Tool calling works; tool errors handled (try a KB query with Phase 2 stopped)
- [ ] Loop/runaway prevention (lower AGENT_MAX_ITERS, watch it stop)
- [ ] Multi-step task using 2+ tools in one question
- [ ] (Next) orchestration / LangGraph, if desired

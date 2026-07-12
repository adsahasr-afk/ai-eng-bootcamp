# Phase 2 - RAG Architecture & Evaluation

A from-scratch Retrieval-Augmented Generation pipeline. Everything except the
final answer runs locally.

## Architecture (the flow)
1. ingest.py   : read sample_docs/ -> chunk -> embed (local) -> store in Chroma
2. /ask        : embed the question -> retrieve top-K chunks -> build a grounded
                 prompt -> Claude answers using ONLY that context, with citations

## Pieces
- rag/chunking.py    fixed-size + overlap chunking (swap strategies here)
- rag/embeddings.py  local sentence-transformers (text stays on your machine)
- rag/store.py       Chroma persistent vector store wrapper
- rag/pipeline.py    retrieve -> prompt -> generate (mock mode until a key is set)
- app/main.py        FastAPI: GET /health, POST /ask
- sample_docs/       synthetic docs (no PII)

## Setup
```bash
cd ~/ai-eng-bootcamp/phase2-rag
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # large: pulls torch, be patient

# reuse your key (optional now; retrieval works without it)
cp .env.example .env                    # then paste your ANTHROPIC_API_KEY
```

## Build the index, then run
```bash
python ingest.py                        # first run downloads the embed model (~90MB)
uvicorn app.main:app --reload --port 8001
```

## Ask
```bash
curl http://127.0.0.1:8001/health       # shows chunks_indexed and mode

curl -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" \
  -d '{"question": "How many days of annual leave do employees get?"}'

curl -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" \
  -d '{"question": "What is reranking and why is it used?"}'
```

## Learning checklist
- [ ] Ingest runs; /health shows chunks_indexed > 0
- [ ] Retrieval returns the right source doc for a question (mock mode)
- [ ] Live grounded answer with citations (after key)
- [ ] Experiment: change CHUNK_SIZE / TOP_K in rag/config.py, re-ingest, compare
- [ ] Ask something NOT in the docs -> confirm it says "I don't know" (faithfulness)
- [ ] (Next) add an eval harness (RAGAS) to score faithfulness & relevancy

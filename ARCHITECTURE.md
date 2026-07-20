# Architecture

Three services built across four phases. One design principle throughout:
**keep data local, and measure everything.** Only the generation call leaves the
machine - chunking, embeddings, vector search and reranking all run locally.

---

## 1. System context

```mermaid
flowchart LR
    subgraph LOCAL["Your machine - WSL2"]
        HELLO["Phase 1<br/>hello-LLM :8000"]
        AGENT["Phase 3<br/>ReAct agent :8002"]
        subgraph DOCKER["Docker container"]
            RAG["Phase 2<br/>RAG service :8001"]
        end
        STORE[("Chroma<br/>vector store")]
        EMB["Embedding model<br/>all-MiniLM-L6-v2"]
    end
    API["Anthropic API<br/>Claude Sonnet 5"]

    AGENT -->|"tool call over HTTP"| RAG
    RAG --> STORE
    RAG --> EMB
    RAG -->|"generation"| API
    AGENT -->|"reasoning + tool use"| API
    HELLO --> API
```

The agent treats the RAG service as just another tool - a clean service
boundary, and the reason Phase 2 and Phase 3 compose instead of merging.

---

## 2. Ingest pipeline

Run once per corpus change: `python ingest.py`

```mermaid
flowchart LR
    DOCS["sample_docs/*.md"] --> CHUNK["chunk_text<br/>500 chars, 80 overlap"]
    CHUNK --> EMBED["Local embeddings<br/>384-dim, batched"]
    EMBED --> STORE[("Chroma<br/>cosine space")]
    META["metadata: source + chunk index"] -.->|"enables citations"| STORE
```

Overlap exists so a fact is never split across a chunk boundary. The `source`
metadata is what lets answers cite the file they came from.

---

## 3. Query path

```mermaid
flowchart LR
    Q["POST /ask"] --> QE["Embed question"]
    QE --> RET["Chroma search<br/>FETCH_K candidates"]
    RET --> DEC{"RERANK?"}
    DEC -->|"off - default"| CUT["Take TOP_K"]
    DEC -->|"on"| CE["Cross-encoder<br/>rescore pairs"]
    CE --> CUT
    CUT --> PROMPT["Grounded prompt<br/>context + cite rule"]
    PROMPT --> LLM["Claude"]
    LLM --> OUT["answer + sources<br/>+ token usage"]
```

Two-stage retrieval: the bi-encoder is fast but approximate, the cross-encoder is
slower but sharper. Reranking is **off by default** - measured on this corpus and
it produced no lift, because the first stage was already near-ceiling. It stays
in the code for when the corpus grows noisier.

---

## 4. Agent orchestration

```mermaid
flowchart LR
    ASK["POST /agent"] --> LOOP["ReAct loop<br/>max_iters guard"]
    LOOP -->|"tool_use"| CALC["calculator"]
    LOOP -->|"tool_use"| KB["knowledge_base_lookup"]
    KB -->|"HTTP"| RAGSVC["RAG service :8001"]
    RAGSVC --> KB
    CALC --> LOOP
    KB --> LOOP
    LOOP -->|"final answer"| RESULT["answer + step trace"]
```

reason -> act -> observe, until the model answers or `MAX_ITERS` trips. Tool
failures return error **strings**, so the model can recover on the next turn
rather than crashing the loop.

---

## 5. Evaluation - two tiers

```mermaid
flowchart TD
    subgraph TIER1["Tier 1 - GitHub Actions, free, no key"]
        PYT["pytest"] --> DET["chunking + metric math + config"]
    end
    subgraph TIER2["Tier 2 - local only, paid"]
        GATE["evaluation.gate"] --> GOLD["golden set + adversarial"]
        GOLD --> PIPE["real RAG pipeline"]
        PIPE --> JUDGE["Claude-as-judge<br/>+ local embeddings"]
        JUDGE --> THRESH{"above thresholds?"}
        THRESH -->|"yes"| OK["exit 0"]
        THRESH -->|"no"| BAD["exit 1"]
    end
```

Deterministic failures are caught free on every push. The expensive quality check
stays local and deliberate, so the API key never reaches a third-party runner.

Metrics: faithfulness, answer relevancy, context precision, context recall,
answer correctness, abstention rate. Thresholds sit just below measured baseline
so ordinary judge noise does not raise false alarms.

---

## 6. Observability

Every call emits one JSON line to stdout - container-friendly, no agent needed.

```mermaid
flowchart LR
    CALL["rag_query"] --> REC["latency, tokens, cost,<br/>sources, status"]
    REC --> OUTS["stdout"]
    OUTS --> LOGS["docker compose logs"]
```

Measured on this system: **cold start ~6.5s** (model load into RAM), **warm ~2s**
(dominated by the Claude call). That gap is why this workload wants a warm,
long-running container rather than scale-to-zero serverless.

Each line records the pricing rates used, so historical cost estimates stay
interpretable after rates change.

---

## Design decisions worth defending

| Decision | Why |
|---|---|
| Local embeddings, not an embeddings API | Document text never leaves the machine |
| Chroma over pgvector | Free, local, zero-ops for this scale; pgvector is the upgrade path |
| Reranking built then disabled | Measured no lift on a small clean corpus - kept for when it changes |
| Chunk 500 / TOP_K 2 | Swept with repeats: chunk size was the dominant lever on faithfulness |
| Structured logs, not Langfuse cloud | Cloud tracing would send prompts off-machine |
| Paid evals local, not in CI | Keeps the API key off third-party runners |
| CPU-only torch, model baked into image | Smaller image, no runtime download, hermetic startup |

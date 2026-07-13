# RAG Eval Results (2026-07-13)

Config: CHUNK_SIZE=500, CHUNK_OVERLAP=80, TOP_K=4

## Aggregate (mean over golden set)

| Metric | Score |
|---|---|
| faithfulness | 0.952 |
| answer_relevancy | 0.747 |
| context_precision | 1.000 |
| context_recall | 1.000 |
| answer_correctness | 0.894 |
| abstention_rate | 1.000 |

## Per-question

| Question | faith | relev | ctx_prec | ctx_rec | correct |
|---|---|---|---|---|---|
| How many days of paid annual leave do employees get? | 1.00 | 0.79 | 1.00 | 1.00 | 0.95 |
| How much does the company reimburse per year for professio | 1.00 | 0.75 | 1.00 | 1.00 | 0.86 |
| What is required for production database access? | 1.00 | 0.73 | 1.00 | 1.00 | 0.87 |
| What does reranking do in a RAG system? | 1.00 | 0.53 | 1.00 | 1.00 | 0.98 |
| Why is overlap used when chunking documents? | 1.00 | 0.79 | 1.00 | 1.00 | 0.88 |
| What does asyncio.gather() do? | 0.67 | 0.82 | 1.00 | 1.00 | 0.80 |
| Is async better for CPU-bound or I/O-bound work? | 1.00 | 0.81 | 1.00 | 1.00 | 0.93 |

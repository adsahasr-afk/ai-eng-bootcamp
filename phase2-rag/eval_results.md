# RAG Eval Results (2026-07-13)

Config: CHUNK_SIZE=200, CHUNK_OVERLAP=40, TOP_K=2

## Aggregate (mean over golden set)

| Metric | Score |
|---|---|
| faithfulness | 0.881 |
| answer_relevancy | 0.740 |
| context_precision | 1.000 |
| context_recall | 1.000 |
| answer_correctness | 0.888 |
| abstention_rate | 1.000 |

## Per-question

| Question | faith | relev | ctx_prec | ctx_rec | correct |
|---|---|---|---|---|---|
| How many days of paid annual leave do employees get? | 1.00 | 0.78 | 1.00 | 1.00 | 0.95 |
| How much does the company reimburse per year for professio | 1.00 | 0.76 | 1.00 | 1.00 | 0.86 |
| What is required for production database access? | 0.67 | 0.73 | 1.00 | 1.00 | 0.87 |
| What does reranking do in a RAG system? | 0.75 | 0.45 | 1.00 | 1.00 | 0.95 |
| Why is overlap used when chunking documents? | 1.00 | 0.82 | 1.00 | 1.00 | 0.88 |
| What does asyncio.gather() do? | 1.00 | 0.91 | 1.00 | 1.00 | 0.80 |
| Is async better for CPU-bound or I/O-bound work? | 0.75 | 0.74 | 1.00 | 1.00 | 0.91 |

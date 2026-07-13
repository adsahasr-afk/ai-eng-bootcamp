# RAG Config Sweep (2026-07-13)

Repeats per config: 2. Cells are mean+/-std across repeats (std ~ judge/generation noise; treat differences smaller than std as not real).

| chunk_size | overlap | n_chunks | top_k | faithfulness | answer_relevancy | context_precision | context_recall | answer_correctness | abstention |
|---|---|---|---|---|---|---|---|---|---|
| 500 | 80 | 7 | 2 | 1.00+/-0.00 | 0.73+/-0.00 | 0.93+/-0.00 | 1.00+/-0.00 | 0.87+/-0.02 | 1.00+/-0.00 |
| 500 | 80 | 7 | 4 | 1.00+/-0.00 | 0.71+/-0.01 | 1.00+/-0.00 | 1.00+/-0.00 | 0.89+/-0.00 | 1.00+/-0.00 |
| 200 | 40 | 14 | 2 | 0.93+/-0.02 | 0.71+/-0.01 | 1.00+/-0.00 | 1.00+/-0.00 | 0.89+/-0.00 | 1.00+/-0.00 |
| 200 | 40 | 14 | 4 | 0.92+/-0.01 | 0.70+/-0.02 | 0.96+/-0.00 | 1.00+/-0.00 | 0.90+/-0.00 | 1.00+/-0.00 |

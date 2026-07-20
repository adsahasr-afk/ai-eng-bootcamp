# Phase 4 - Containerization & Observability

## Build and run

```bash
cd ~/ai-eng-bootcamp/phase2-rag

docker compose build          # first build is slow (torch + model bake)

# Build the vector index into the mounted volume (one time, or after doc changes)
docker compose run --rm rag python ingest.py

docker compose up             # service on http://127.0.0.1:8001
```

Test it:
```bash
curl http://127.0.0.1:8001/health
curl -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" -d '{"question":"How many days of annual leave do employees get?"}'
```

## Observability

Every call emits one JSON line to stdout. Watch them live:

```bash
docker compose logs -f rag
# pretty-print if you have jq:
docker compose logs -f rag | grep rag_query | jq .
```

A line looks like:
```json
{"event":"rag_query","request_id":"a1b2c3","top_k":2,"rerank":false,
 "sources":["company_handbook.md"],"n_chunks":2,"mode":"live",
 "input_tokens":701,"output_tokens":39,"status":"ok",
 "latency_ms":1423.7,"est_cost_usd":0.0018,
 "rates_usd_per_m":{"in":2.0,"out":10.0}}
```

That is the raw material of LLMOps: latency (p95s), token usage and cost per
request, which sources were retrieved, and error rates. Failures are logged too,
with `status":"error"` and the exception.

Also log to a file with `OBS_LOG_FILE=/app/obs.log`.

## Cost estimates - IMPORTANT, rates change 2026-09-01

`est_cost_usd` is an ESTIMATE for relative signal (which queries are expensive,
is cost trending up) - it is NOT billing truth. The authoritative number is the
usage/billing page in the Anthropic Console.

Defaults assume **Claude Sonnet 5 introductory pricing: $2 / $10 per 1M
input/output tokens, which is in effect only through 2026-08-31.**

    >>> ACTION REQUIRED on 2026-09-01: standard pricing becomes $3 / $15. <<<

Update in `.env` when that happens:
```bash
INPUT_USD_PER_M=3.0
OUTPUT_USD_PER_M=15.0
```

Three things the estimate does not know:
- **Model.** These rates are Sonnet 5. Switch ANTHROPIC_MODEL to Opus or Haiku
  and the constants are wrong.
- **Prompt caching** (up to ~90% savings) and **batch processing** (~50%) - your
  real invoice may be LOWER than the estimate.
- Anything about your actual account tier or discounts.

Each log line records the rates it used (`rates_usd_per_m`), so historical logs
remain interpretable after a price change. Verify current rates at
docs.claude.com/en/docs/about-claude/pricing.

## Image notes
- CPU-only torch keeps the image from pulling multi-GB CUDA wheels.
- The embedding model is baked in at build, so startup needs no network.
- `.env` is in `.dockerignore` - the key is injected at runtime via `env_file`,
  never baked into a layer. (Anything COPYed into an image is extractable.)

## BEFORE you expose this publicly
This endpoint proxies a paid LLM. A public URL with no controls = anyone can
drain your credit. Per your pre-deploy checklist, add first:
- [ ] An auth check (API key header) on /ask
- [ ] Rate limiting per IP/key
- [ ] Anthropic spend cap set (already done) + alerting
- [ ] CORS scoped to known origins, not *
- [ ] No secrets in the image (verified above)

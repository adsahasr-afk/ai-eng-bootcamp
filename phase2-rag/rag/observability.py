"""Structured JSON logging - the foundation of observability.

Emits ONE JSON line per LLM call to stdout (container-friendly; `docker compose
logs` picks it up) and optionally to a file. Captures what you actually need to
debug and cost-manage a RAG service: latency, tokens, estimated cost, and which
sources were retrieved.

This is deliberately dependency-free. A tracing UI (Langfuse etc.) can be layered
on later - but if you don't know WHAT to record, a fancy UI won't save you.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from contextlib import contextmanager

# Introductory API rates, USD per 1M tokens. Verify at docs.anthropic.com/pricing
INPUT_USD_PER_M = float(os.getenv("INPUT_USD_PER_M", "2.0"))
OUTPUT_USD_PER_M = float(os.getenv("OUTPUT_USD_PER_M", "10.0"))
LOG_FILE = os.getenv("OBS_LOG_FILE", "")

_logger = logging.getLogger("rag.obs")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    _stream = logging.StreamHandler(sys.stdout)
    _stream.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_stream)
    if LOG_FILE:
        _file = logging.FileHandler(LOG_FILE)
        _file.setFormatter(logging.Formatter("%(message)s"))
        _logger.addHandler(_file)
    _logger.propagate = False


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Rough USD cost for one call. Rates are configurable via env."""
    return round(
        input_tokens / 1_000_000 * INPUT_USD_PER_M
        + output_tokens / 1_000_000 * OUTPUT_USD_PER_M,
        6,
    )


def log_event(**fields) -> None:
    _logger.info(json.dumps(fields, default=str))


@contextmanager
def track(event: str, **base):
    """Time a block and emit one JSON log line - including on failure.

    Usage:
        with track("rag_query", top_k=2) as rec:
            ...
            rec["input_tokens"] = 123     # fields added here get logged too
    """
    rec = {
        "event": event,
        "request_id": base.pop("request_id", None) or uuid.uuid4().hex[:12],
        **base,
    }
    t0 = time.perf_counter()
    try:
        yield rec
        rec.setdefault("status", "ok")
    except Exception as e:  # noqa: BLE001
        rec["status"] = "error"
        rec["error"] = f"{type(e).__name__}: {e}"
        raise
    finally:
        rec["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        if "input_tokens" in rec and "output_tokens" in rec:
            rec["est_cost_usd"] = estimate_cost(rec["input_tokens"], rec["output_tokens"])
            # Record the rates used, so historical log lines stay interpretable
            # after prices change. Sonnet 5 introductory rates end 2026-08-31;
            # from 2026-09-01 the standard rate is 3.0 / 15.0 per 1M tokens.
            rec["rates_usd_per_m"] = {"in": INPUT_USD_PER_M, "out": OUTPUT_USD_PER_M}
        log_event(**rec)

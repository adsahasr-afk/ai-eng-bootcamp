"""Claude-as-judge helpers.

Grading uses your Anthropic key. Similarity uses LOCAL embeddings, so document
text stays on your machine except for the judge calls you opt into by running
the eval. Heavy imports are lazy so this module loads fast.
"""
from __future__ import annotations

import json
import re

from rag.config import ANTHROPIC_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic  # lazy
        _client = Anthropic()
    return _client


def _extract_json(text: str):
    """Pull a JSON object/array out of a model reply, tolerating ``` fences."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    raw = fenced.group(1).strip() if fenced else text.strip()
    # trim to the first { or [ so leading prose doesn't break parsing
    candidates = [i for i in (raw.find("{"), raw.find("[")) if i != -1]
    if candidates:
        raw = raw[min(candidates):]
    return json.loads(raw)


def judge_json(system: str, user: str, max_tokens: int = 1024) -> dict:
    """Call Claude and return parsed JSON. On parse failure, warn and return {}."""
    msg = _get_client().messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    try:
        data = _extract_json(text)
        return data if isinstance(data, dict) else {"_list": data}
    except Exception as e:  # noqa: BLE001
        print(f"  [judge warning] could not parse JSON ({e}); got: {text[:120]!r}")
        return {}

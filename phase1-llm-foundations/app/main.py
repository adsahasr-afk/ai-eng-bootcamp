"""Hello LLM - a minimal FastAPI wrapper around the Anthropic Messages API.

Endpoints:
  GET  /health  - liveness + whether the API key is loaded (mock vs live)
  POST /chat    - send a message, get a reply + token usage
"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()  # reads .env from the working directory

# Verify the exact current model string at docs.anthropic.com/en/docs/about-claude/models
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

app = FastAPI(title="Hello LLM", version="0.1.0")

# Auto-detect mode: no key -> offline mock (build/test today, no cost).
# Add a key to .env later and the real API call kicks in automatically.
HAS_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))
client = Anthropic() if HAS_KEY else None


class ChatRequest(BaseModel):
    message: str
    system: str | None = None
    max_tokens: int = 512


class ChatResponse(BaseModel):
    reply: str
    model: str
    input_tokens: int
    output_tokens: int
    mock: bool = False


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL,
        "key_loaded": HAS_KEY,
        "mode": "live" if HAS_KEY else "mock",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # ---- Offline mock: no key yet, so echo a canned reply. Zero cost. ----
    if not HAS_KEY:
        preview = req.message.strip()[:80]
        return ChatResponse(
            reply=(
                "[MOCK REPLY - no API key set] I received your message: "
                f'"{preview}". Add ANTHROPIC_API_KEY to .env and restart to get '
                "a real Claude response."
            ),
            model="mock",
            input_tokens=len(req.message.split()),
            output_tokens=0,
            mock=True,
        )

    # ---- Live: real Anthropic call ----
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=req.max_tokens,
            system=req.system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": req.message}],
        )
    except Exception as e:  # noqa: BLE001 - surface any API error to the caller
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {e}")

    reply = "".join(block.text for block in msg.content if block.type == "text")
    return ChatResponse(
        reply=reply,
        model=msg.model,
        input_tokens=msg.usage.input_tokens,
        output_tokens=msg.usage.output_tokens,
        mock=False,
    )

"""Phase 3 - Agent API. A ReAct agent with tools, exposed over HTTP."""
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from agent.config import ANTHROPIC_MODEL, MAX_ITERS  # noqa: E402
from agent.loop import run_agent                      # noqa: E402

app = FastAPI(title="Agent - Phase 3", version="0.1.0")


class AgentRequest(BaseModel):
    question: str
    max_iters: int = MAX_ITERS


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": ANTHROPIC_MODEL,
        "mode": "live" if os.getenv("ANTHROPIC_API_KEY") else "mock",
        "max_iters": MAX_ITERS,
    }


@app.post("/agent")
def agent(req: AgentRequest):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {
            "answer": "[MOCK - no API key] Add ANTHROPIC_API_KEY to .env for a real agent run.",
            "steps": [],
            "mock": True,
        }
    return run_agent(req.question, req.max_iters)

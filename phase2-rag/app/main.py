"""Phase 2 - RAG API. A retrieval-augmented /ask endpoint over your local docs."""
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from rag.config import ANTHROPIC_MODEL, TOP_K  # noqa: E402
from rag.pipeline import answer_question         # noqa: E402
from rag.store import count                       # noqa: E402

app = FastAPI(title="RAG - Phase 2", version="0.1.0")


class AskRequest(BaseModel):
    question: str
    top_k: int = TOP_K


@app.get("/health")
def health():
    try:
        n = count()
    except Exception:
        n = 0
    return {
        "status": "ok",
        "model": ANTHROPIC_MODEL,
        "mode": "live" if os.getenv("ANTHROPIC_API_KEY") else "mock",
        "chunks_indexed": n,
    }


@app.post("/ask")
def ask(req: AskRequest):
    return answer_question(req.question, req.top_k)

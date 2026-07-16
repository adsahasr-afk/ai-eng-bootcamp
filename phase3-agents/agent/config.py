"""Agent settings."""
import os

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
MAX_ITERS = int(os.getenv("AGENT_MAX_ITERS", "6"))   # runaway guard
# The knowledge_base_lookup tool calls your Phase 2 RAG service:
RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8001/ask")

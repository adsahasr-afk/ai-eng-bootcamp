"""Central settings for the RAG pipeline. Tune these to see behavior change."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "sample_docs"       # source documents (committed)
CHROMA_DIR = BASE_DIR / ".chroma"         # persistent vector store (gitignored)
COLLECTION = "bootcamp_docs"

# Local embedding model: 384-dim, fast, free, runs on your machine.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking (characters). Smaller = more precise retrieval, less context per hit.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

# Retrieval: how many chunks to pull per question.
TOP_K = 4

# Generation reuses your Phase 1 Anthropic setup.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

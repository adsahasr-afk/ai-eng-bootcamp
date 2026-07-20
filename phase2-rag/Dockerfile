# Phase 4: containerized RAG service.
#
# Two size/speed decisions worth understanding:
#  1. CPU-only torch  - the default torch wheel pulls multi-GB CUDA libraries you
#     will never use on a CPU host. The CPU index keeps the image far smaller.
#  2. Bake the embedding model into the image at build time, so the container
#     starts fast and needs no network at runtime.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch BEFORE requirements, so sentence-transformers reuses it
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8001

# NOTE: no --reload in a container; that is a dev-only convenience.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

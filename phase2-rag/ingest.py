"""Load every file in sample_docs/ into the vector store: chunk -> embed -> store.

Run:  python ingest.py
Re-running rebuilds the collection from scratch.
"""
from __future__ import annotations

import chromadb

from rag.chunking import chunk_text
from rag.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION, DATA_DIR
from rag.embeddings import embed_texts


def main() -> None:
    files = sorted(p for p in DATA_DIR.glob("*") if p.suffix in {".md", ".txt"})
    if not files:
        print(f"No .md/.txt files found in {DATA_DIR}")
        return

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION)  # fresh rebuild
    except Exception:
        pass
    col = client.get_or_create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    total = 0
    for f in files:
        chunks = chunk_text(f.read_text(encoding="utf-8"), CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            continue
        embeddings = embed_texts(chunks)
        ids = [f"{f.stem}-{i}" for i in range(len(chunks))]
        metas = [{"source": f.name, "chunk": i} for i in range(len(chunks))]
        col.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metas)
        total += len(chunks)
        print(f"  {f.name}: {len(chunks)} chunks")

    print(f"Done. Indexed {total} chunks from {len(files)} files into '{COLLECTION}'.")


if __name__ == "__main__":
    main()

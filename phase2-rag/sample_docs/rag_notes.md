# Retrieval-Augmented Generation (RAG) Notes

RAG combines a retriever with a generator. The retriever finds relevant text
chunks from a knowledge base using vector similarity search, and the generator
(an LLM) produces an answer grounded in those chunks.

Chunking splits documents into smaller passages. Common strategies are
fixed-size, sentence-based, recursive, and semantic chunking. Overlap between
chunks prevents a fact from being split across a boundary.

Embeddings convert text into numeric vectors so that semantically similar text
has nearby vectors. The all-MiniLM-L6-v2 model produces 384-dimensional
embeddings.

Faithfulness measures whether the generated answer is supported by the retrieved
context. A common failure is hallucination, where the model invents facts that
are not present in the context.

Reranking reorders retrieved chunks by relevance using a cross-encoder, which
improves precision before the generation step.

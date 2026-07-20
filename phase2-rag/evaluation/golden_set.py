"""Golden evaluation set: labeled questions over the synthetic docs.

Each item has the question, the expected (reference) answer, and the source
file the answer should come from. This lets us measure reference-based metrics
(correctness, context recall) and catch regressions when tuning chunking/TOP_K.
"""

GOLDEN = [
    {
        "question": "How many days of paid annual leave do employees get?",
        "expected_answer": "Employees get 25 days of paid annual leave per year, plus public holidays.",
        "expected_source": "company_handbook.md",
    },
    {
        "question": "How much does the company reimburse per year for professional development?",
        "expected_answer": "Up to 1000 dollars per year for professional development.",
        "expected_source": "company_handbook.md",
    },
    {
        "question": "What is required for production database access?",
        "expected_answer": "Two-factor authentication; all access is logged for audit purposes.",
        "expected_source": "company_handbook.md",
    },
    {
        "question": "What does reranking do in a RAG system?",
        "expected_answer": "Reranking reorders retrieved chunks by relevance using a cross-encoder to improve precision before generation.",
        "expected_source": "rag_notes.md",
    },
    {
        "question": "Why is overlap used when chunking documents?",
        "expected_answer": "Overlap prevents a fact from being split across a chunk boundary.",
        "expected_source": "rag_notes.md",
    },
    {
        "question": "What does asyncio.gather() do?",
        "expected_answer": "It runs multiple coroutines concurrently and collects their results into a list.",
        "expected_source": "python_async.md",
    },
    {
        "question": "Is async better for CPU-bound or I/O-bound work?",
        "expected_answer": "Async is best for I/O-bound work such as network calls, not CPU-bound work.",
        "expected_source": "python_async.md",
    },
]

# Questions whose answers are NOT in the docs. A faithful system should abstain
# ("I don't know") instead of hallucinating. Tests hallucination-resistance.
ADVERSARIAL = [
    "What is the company's parental leave policy?",
    "In which programming language was Acme Robotics' first product written?",
       "How many employees does Acme Robotics have?",
    "What is the company's stock ticker symbol?",
]

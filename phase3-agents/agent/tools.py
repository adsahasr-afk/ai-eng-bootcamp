"""Agent tools. Each returns a STRING (what the model sees as the tool result).
Every failure is caught and returned as a readable error string, so the agent
can react on the next turn instead of crashing.
"""
from __future__ import annotations

import ast
import operator

import httpx

from agent.config import RAG_URL

# Tool schemas advertised to Claude's tool-use API.
TOOL_SCHEMAS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression (+, -, *, /, //, %, **, parentheses). Use for any math.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. (25 + 5) * 3"}},
            "required": ["expression"],
        },
    },
    {
        "name": "knowledge_base_lookup",
        "description": "Look up facts from the internal knowledge base (company handbook, RAG notes, async notes) via the Phase 2 RAG service. Use for company/policy/technical questions.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "a natural-language question"}},
            "required": ["query"],
        },
    },
]

# ---- safe calculator (no eval/exec) ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numbers allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as e:  # noqa: BLE001
        return f"Error: invalid expression ({e})"


def knowledge_base_lookup(query: str) -> str:
    try:
        r = httpx.post(RAG_URL, json={"question": query}, timeout=30)
        r.raise_for_status()
        data = r.json()
        answer = data.get("answer", "")
        sources = ", ".join(data.get("sources", []))
        return f"{answer}\n(sources: {sources})"
    except Exception as e:  # noqa: BLE001
        return (f"Error: knowledge base unavailable ({e}). "
                "Is the Phase 2 RAG service running on port 8001?")


def dispatch(name: str, args: dict) -> str:
    """Route a tool call to its function, catching any error as a string."""
    try:
        if name == "calculator":
            return calculator(args["expression"])
        if name == "knowledge_base_lookup":
            return knowledge_base_lookup(args["query"])
        return f"Error: unknown tool '{name}'"
    except Exception as e:  # noqa: BLE001
        return f"Error running {name}: {e}"

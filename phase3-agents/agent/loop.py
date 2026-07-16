"""From-scratch ReAct loop on Claude's native tool-use API.

reason -> act -> observe, repeated until the model returns a final answer or we
hit MAX_ITERS (the runaway guard). Tool errors are strings, so the model can
recover on the next turn rather than crashing the loop.
"""
from __future__ import annotations

from anthropic import Anthropic

from agent.config import ANTHROPIC_MODEL, MAX_ITERS
from agent.tools import TOOL_SCHEMAS, dispatch

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools. Think step by step and "
    "use a tool whenever it helps. Use the calculator for arithmetic and the "
    "knowledge_base_lookup for company/policy/technical facts. When you have "
    "enough information, give a concise final answer."
)


def run_agent(question: str, max_iters: int = MAX_ITERS) -> dict:
    client = Anthropic()
    messages = [{"role": "user", "content": question}]
    trace = []

    for step in range(1, max_iters + 1):
        msg = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": msg.content})

        if msg.stop_reason != "tool_use":
            answer = "".join(b.text for b in msg.content if b.type == "text")
            return {"answer": answer, "steps": trace, "iterations": step, "stopped": "final"}

        tool_results = []
        for block in msg.content:
            if block.type == "tool_use":
                result = dispatch(block.name, block.input)
                trace.append({"tool": block.name, "input": block.input, "result": result})
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    return {
        "answer": "[stopped: reached max iterations without a final answer]",
        "steps": trace,
        "iterations": max_iters,
        "stopped": "max_iters",
    }

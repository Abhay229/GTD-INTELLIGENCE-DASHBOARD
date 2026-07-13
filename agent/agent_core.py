"""
Core agent loop: an LLM (via OpenRouter) that can call the tools in
tools/agent_tools.py to answer analytical questions about the GTD dataset.

This is a hand-rolled tool-calling loop (rather than a framework like
LangChain) so the mechanics are fully visible:

    1. Send the conversation + tool schemas to the model.
    2. If the model requests a tool call -> execute the matching Python
       function -> feed the result back to the model as a "tool" message.
    3. Repeat until the model responds with plain text (no more tool calls)
       or a safety iteration cap is hit.

Every step is appended to `reasoning_trace` so the UI can show *why* the
agent did what it did (basic observability for an agentic system).
"""

import json
import time
from agent.llm_client import get_client, DEFAULT_MODEL, is_configured
from tools.agent_tools import TOOL_REGISTRY, TOOL_SCHEMAS

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are an intelligence analyst assistant for a terrorism
data dashboard (Global Terrorism Database). You have access to tools that
query real data, run a trend forecast, and run a trained threat-level
classifier. Use tools whenever the user's question requires actual data or
predictions rather than general knowledge. Do not fabricate statistics -
call a tool to get them. When you have enough information, give a clear,
concise, well-organized answer. Always mention which countries/years/tools
your answer is based on."""


def run_agent(user_message: str, chat_history: list = None) -> dict:
    """
    Run the agent loop for a single user message.

    Parameters
    ----------
    user_message : str
    chat_history : list of {"role": ..., "content": ...} dicts (prior turns)

    Returns
    -------
    dict with keys: "answer" (str) and "trace" (list of step dicts)
    """
    if not is_configured():
        return {
            "answer": (
                "⚠️ No OpenRouter API key configured. Add `OPENROUTER_API_KEY` "
                "to a `.env` file (see `.env.example`) to enable the agent."
            ),
            "trace": [],
        }

    client = get_client()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    trace = []

    for iteration in range(MAX_TOOL_ITERATIONS):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
        except Exception as e:
            trace.append({"step": iteration, "event": "llm_error", "detail": str(e)})
            return {
                "answer": f"The model call failed: {e}",
                "trace": trace,
            }

        msg = response.choices[0].message
        elapsed = round(time.time() - t0, 2)

        tool_calls = getattr(msg, "tool_calls", None)

        if not tool_calls:
            # Final answer - no more tools requested
            trace.append({
                "step": iteration,
                "event": "final_answer",
                "elapsed_sec": elapsed,
            })
            return {"answer": msg.content, "trace": trace}

        # Model wants to call one or more tools
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                fn_args = {}

            trace.append({
                "step": iteration,
                "event": "tool_call",
                "tool": fn_name,
                "arguments": fn_args,
                "elapsed_sec": elapsed,
            })

            tool_fn = TOOL_REGISTRY.get(fn_name)
            if tool_fn is None:
                result = {"error": f"Unknown tool '{fn_name}'"}
            else:
                try:
                    result = tool_fn(**fn_args)
                except Exception as e:
                    result = {"error": f"Tool execution failed: {e}"}

            trace.append({
                "step": iteration,
                "event": "tool_result",
                "tool": fn_name,
                "result": result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, default=str),
            })

    trace.append({"step": MAX_TOOL_ITERATIONS, "event": "max_iterations_reached"})
    return {
        "answer": (
            "I wasn't able to finish reasoning within the tool-call limit. "
            "Try asking a more specific question."
        ),
        "trace": trace,
    }

"""
Agent orchestrator — the tool-use loop.

Takes a user message, sends it to the LLM with tool definitions,
executes any tool calls, feeds results back, and repeats until
the LLM produces a final text response.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

from app.agent.providers.base import LLMProvider
from app.agent.providers.anthropic import AnthropicProvider
from app.agent.providers.openai import OpenAIProvider
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.agent.prompts import build_system_prompt
from app.agent.memory.feedback import FeedbackStore
from app.config import settings


MAX_TOOL_ROUNDS = 5

_feedback_store = FeedbackStore()


def get_provider() -> LLMProvider:
    """Get the configured LLM provider."""
    if settings.default_provider == "openai":
        return OpenAIProvider()
    return AnthropicProvider()


async def _build_prompt(calculator_state: dict[str, Any] | None = None) -> str:
    """Build the system prompt with all memory layers."""
    learned_patterns = await _feedback_store.get_active_patterns()
    return build_system_prompt(
        session_context=calculator_state,
        learned_patterns=learned_patterns if learned_patterns else None,
    )


async def run_agent(
    user_message: str,
    history: list[dict] | None = None,
    calculator_state: dict[str, Any] | None = None,
) -> dict:
    """
    Non-streaming agent loop. Runs tool calls until the LLM gives a final answer.

    Returns:
        {
            "response": str,
            "tool_calls": list[dict],  # tools that were executed
        }
    """
    provider = get_provider()
    system_prompt = await _build_prompt(calculator_state)
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})

    executed_tools = []

    for _ in range(MAX_TOOL_ROUNDS):
        result = await provider.chat_with_tools(messages, TOOL_DEFINITIONS, system_prompt)

        if not result["tool_calls"]:
            return {"response": result["content"], "tool_calls": executed_tools}

        # Build assistant message with tool calls
        assistant_msg = {"role": "assistant", "content": result["content"]}
        if settings.default_provider == "openai" and "tool_calls_raw" in result:
            assistant_msg["tool_calls_raw"] = result["tool_calls_raw"]
        elif settings.default_provider == "anthropic":
            # For Anthropic, build content blocks
            content_blocks = []
            if result["content"]:
                content_blocks.append({"type": "text", "text": result["content"]})
            for tc in result["tool_calls"]:
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"],
                })
            assistant_msg = {"role": "assistant", "content": content_blocks}

        messages.append(assistant_msg)

        # Execute each tool call
        for tc in result["tool_calls"]:
            try:
                tool_result = execute_tool(tc["name"], tc["arguments"], calculator_state)
                executed_tools.append({
                    "name": tc["name"],
                    "arguments": tc["arguments"],
                    "result": tool_result,
                })
            except Exception as e:
                tool_result = {"error": str(e)}
                executed_tools.append({
                    "name": tc["name"],
                    "arguments": tc["arguments"],
                    "error": str(e),
                })

            messages.append({
                "role": "tool_result",
                "tool_use_id": tc["id"],
                "content": tool_result,
            })

    return {"response": "I've hit the maximum number of calculation steps. Here's what I found so far.", "tool_calls": executed_tools}


async def stream_agent(
    user_message: str,
    history: list[dict] | None = None,
    calculator_state: dict[str, Any] | None = None,
) -> AsyncIterator[dict]:
    """
    Streaming agent loop. Yields events as they happen:
        {"type": "text", "content": "..."}
        {"type": "tool_start", "name": "...", "arguments": {...}}
        {"type": "tool_result", "name": "...", "result": {...}}
        {"type": "done"}
    """
    provider = get_provider()
    system_prompt = await _build_prompt(calculator_state)
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})

    for _ in range(MAX_TOOL_ROUNDS):
        tool_calls_in_round = []
        text_parts = []

        async for chunk in provider.stream_chat_with_tools(messages, TOOL_DEFINITIONS, system_prompt):
            if chunk["type"] == "text":
                yield chunk
                text_parts.append(chunk["content"])
            elif chunk["type"] == "tool_use":
                tool_calls_in_round.append(chunk)
            elif chunk["type"] == "done":
                pass

        if not tool_calls_in_round:
            yield {"type": "done"}
            return

        # Build assistant message
        full_text = "".join(text_parts)
        if settings.default_provider == "anthropic":
            content_blocks = []
            if full_text:
                content_blocks.append({"type": "text", "text": full_text})
            for tc in tool_calls_in_round:
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"],
                })
            messages.append({"role": "assistant", "content": content_blocks})
        else:
            messages.append({
                "role": "assistant",
                "content": full_text,
                "tool_calls_raw": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for tc in tool_calls_in_round
                ],
            })

        # Execute tool calls
        for tc in tool_calls_in_round:
            yield {"type": "tool_start", "name": tc["name"], "arguments": tc["arguments"]}

            try:
                tool_result = execute_tool(tc["name"], tc["arguments"], calculator_state)
                yield {"type": "tool_result", "name": tc["name"], "result": tool_result}
            except Exception as e:
                tool_result = {"error": str(e)}
                yield {"type": "tool_error", "name": tc["name"], "error": str(e)}

            messages.append({
                "role": "tool_result",
                "tool_use_id": tc["id"],
                "content": tool_result,
            })

    yield {"type": "done"}

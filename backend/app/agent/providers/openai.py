from __future__ import annotations

import json
from typing import AsyncIterator

from openai import AsyncOpenAI

from .base import LLMProvider
from app.config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert to OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in tools
        ]

    def _convert_messages(self, messages: list[dict], system_prompt: str) -> list[dict]:
        """Convert to OpenAI message format."""
        converted = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            if msg["role"] == "tool_result":
                converted.append({
                    "role": "tool",
                    "tool_call_id": msg["tool_use_id"],
                    "content": json.dumps(msg["content"]) if isinstance(msg["content"], dict) else str(msg["content"]),
                })
            elif msg["role"] == "assistant" and "tool_calls_raw" in msg:
                converted.append({
                    "role": "assistant",
                    "content": msg.get("content", ""),
                    "tool_calls": msg["tool_calls_raw"],
                })
            else:
                converted.append({"role": msg["role"], "content": msg.get("content", "")})
        return converted

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(messages, system_prompt),
            tools=self._convert_tools(tools),
        )

        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        tool_calls_raw = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })
                tool_calls_raw.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                })

        return {
            "content": message.content or "",
            "tool_calls": tool_calls,
            "tool_calls_raw": tool_calls_raw,
            "stop_reason": choice.finish_reason,
        }

    async def stream_chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> AsyncIterator[dict]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(messages, system_prompt),
            tools=self._convert_tools(tools),
            stream=True,
        )

        tool_calls_buffer = {}

        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            finish_reason = chunk.choices[0].finish_reason if chunk.choices else None

            if delta:
                if delta.content:
                    yield {"type": "text", "content": delta.content}

                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_buffer:
                            tool_calls_buffer[idx] = {
                                "id": tc_delta.id or "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc_delta.id:
                            tool_calls_buffer[idx]["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_buffer[idx]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_buffer[idx]["arguments"] += tc_delta.function.arguments

            if finish_reason == "tool_calls":
                for idx in sorted(tool_calls_buffer.keys()):
                    tc = tool_calls_buffer[idx]
                    try:
                        arguments = json.loads(tc["arguments"]) if tc["arguments"] else {}
                    except json.JSONDecodeError:
                        arguments = {}
                    yield {
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "arguments": arguments,
                    }
                tool_calls_buffer = {}

            if finish_reason == "stop":
                yield {"type": "done", "stop_reason": "end_turn"}
            elif finish_reason == "tool_calls":
                yield {"type": "done", "stop_reason": "tool_use"}

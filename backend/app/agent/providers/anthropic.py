from __future__ import annotations

import json
from typing import AsyncIterator

import anthropic

from .base import LLMProvider
from app.config import settings


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = model or settings.model_name

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert our tool format to Anthropic's format."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": {
                    "type": "object",
                    "properties": tool["parameters"].get("properties", {}),
                    "required": tool["parameters"].get("required", []),
                },
            }
            for tool in tools
        ]

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert to Anthropic message format."""
        converted = []
        for msg in messages:
            if msg["role"] == "tool_result":
                converted.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_use_id"],
                            "content": json.dumps(msg["content"]) if isinstance(msg["content"], dict) else str(msg["content"]),
                        }
                    ],
                })
            else:
                converted.append(msg)
        return converted

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> dict:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=self._convert_messages(messages),
            tools=self._convert_tools(tools),
        )

        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })

        return {
            "content": "".join(text_parts),
            "tool_calls": tool_calls,
            "stop_reason": response.stop_reason,
        }

    async def stream_chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> AsyncIterator[dict]:
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=self._convert_messages(messages),
            tools=self._convert_tools(tools),
        ) as stream:
            current_tool = None
            current_json = ""

            async for event in stream:
                if event.type == "content_block_start":
                    if hasattr(event.content_block, "type"):
                        if event.content_block.type == "text":
                            pass
                        elif event.content_block.type == "tool_use":
                            current_tool = {
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                            }
                            current_json = ""

                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield {"type": "text", "content": event.delta.text}
                    elif hasattr(event.delta, "partial_json"):
                        current_json += event.delta.partial_json

                elif event.type == "content_block_stop":
                    if current_tool:
                        try:
                            arguments = json.loads(current_json) if current_json else {}
                        except json.JSONDecodeError:
                            arguments = {}
                        yield {
                            "type": "tool_use",
                            "id": current_tool["id"],
                            "name": current_tool["name"],
                            "arguments": arguments,
                        }
                        current_tool = None
                        current_json = ""

                elif event.type == "message_stop":
                    yield {"type": "done", "stop_reason": "end_turn"}

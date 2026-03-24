from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Any


class LLMProvider(ABC):
    """Abstract base for LLM providers (Claude, OpenAI)."""

    @abstractmethod
    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> dict:
        """
        Send messages + tools to the LLM and get a response.

        Returns a dict with:
            - "content": str (text response, may be empty if tool_use)
            - "tool_calls": list[dict] with "name", "arguments", "id"
            - "stop_reason": str ("end_turn", "tool_use", etc.)
        """
        ...

    @abstractmethod
    async def stream_chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> AsyncIterator[dict]:
        """
        Stream response chunks. Each chunk is a dict:
            - {"type": "text", "content": "..."} for text deltas
            - {"type": "tool_use", "name": "...", "arguments": {...}, "id": "..."} for tool calls
            - {"type": "done", "stop_reason": "..."}
        """
        ...

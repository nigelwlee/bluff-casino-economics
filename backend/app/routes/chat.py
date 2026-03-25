from __future__ import annotations

import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import ChatRequest
from app.agent.orchestrator import stream_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(req: ChatRequest):
    """SSE streaming chat endpoint. Streams agent responses as server-sent events."""

    history = [{"role": m.role, "content": m.content} for m in req.history]

    async def event_generator():
        async for event in stream_agent(req.message, history, req.calculator_state):
            if event["type"] == "text":
                yield {
                    "event": "text",
                    "data": json.dumps({"content": event["content"]}),
                }
            elif event["type"] == "tool_start":
                yield {
                    "event": "tool_start",
                    "data": json.dumps({
                        "name": event["name"],
                        "arguments": event["arguments"],
                    }),
                }
            elif event["type"] == "tool_result":
                yield {
                    "event": "tool_result",
                    "data": json.dumps({
                        "name": event["name"],
                        "result": event["result"],
                    }),
                }
            elif event["type"] == "tool_error":
                yield {
                    "event": "tool_error",
                    "data": json.dumps({
                        "name": event["name"],
                        "error": event["error"],
                    }),
                }
            elif event["type"] == "done":
                yield {
                    "event": "done",
                    "data": json.dumps({}),
                }

    return EventSourceResponse(event_generator())

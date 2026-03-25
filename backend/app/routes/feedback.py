from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import FeedbackRequest
from app.agent.memory.feedback import FeedbackStore

router = APIRouter(prefix="/api", tags=["feedback"])

_store = FeedbackStore()


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Save a feedback snapshot (calculator state + chat history + optional note)."""
    chat_history = [{"role": m.role, "content": m.content} for m in req.chat_history]
    feedback_id = await _store.save_feedback(
        calculator_state=req.calculator_state or {},
        chat_history=chat_history,
        user_note=req.user_note,
    )
    return {"id": feedback_id, "status": "recorded"}


@router.get("/feedback")
async def list_feedback(limit: int = 50):
    """List recent feedback entries (admin)."""
    entries = await _store.list_feedback(limit=limit)
    return {"feedback": entries}

"""
Layer 4: Feedback learning — persists user feedback and learned patterns in SQLite.
"""
from __future__ import annotations

import json
import aiosqlite
from datetime import datetime, timezone

from app.storage.sqlite_store import DB_PATH


class FeedbackStore:
    """Manages feedback and learned_patterns tables in bluff.db."""

    async def _init_db(self) -> None:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    calculator_state TEXT NOT NULL,
                    chat_history TEXT NOT NULL,
                    user_note TEXT,
                    created_at TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    source_feedback_ids TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1
                )
            """)
            await db.commit()

    async def save_feedback(
        self,
        calculator_state: dict,
        chat_history: list[dict],
        user_note: str | None = None,
    ) -> int:
        """Save a feedback snapshot. Returns the feedback id."""
        await self._init_db()
        created_at = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "INSERT INTO feedback (calculator_state, chat_history, user_note, created_at) VALUES (?, ?, ?, ?)",
                (
                    json.dumps(calculator_state or {}),
                    json.dumps(chat_history or []),
                    user_note,
                    created_at,
                ),
            )
            await db.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    async def get_active_patterns(self, limit: int = 20) -> list[str]:
        """Return active learned patterns for injection into the system prompt."""
        await self._init_db()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT pattern FROM learned_patterns WHERE active = 1 ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def list_feedback(self, limit: int = 50) -> list[dict]:
        """List recent feedback entries (for admin review)."""
        await self._init_db()
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT id, calculator_state, chat_history, user_note, created_at, resolved FROM feedback ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "calculator_state": json.loads(row["calculator_state"]),
                        "chat_history": json.loads(row["chat_history"]),
                        "user_note": row["user_note"],
                        "created_at": row["created_at"],
                        "resolved": bool(row["resolved"]),
                    }
                    for row in rows
                ]

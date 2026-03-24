from __future__ import annotations

import json
import aiosqlite
from datetime import datetime, timezone
from nanoid import generate as nanoid


DB_PATH = "bluff.db"


class ScenarioStore:
    async def _init_db(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    chat_history TEXT NOT NULL,
                    calc_results TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            await db.commit()

    async def save(self, name: str, chat_history: list, calc_results: list) -> dict:
        await self._init_db()
        scenario_id = nanoid(size=10)
        created_at = datetime.now(timezone.utc).isoformat()

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO scenarios (id, name, chat_history, calc_results, created_at) VALUES (?, ?, ?, ?, ?)",
                (scenario_id, name, json.dumps(chat_history), json.dumps(calc_results), created_at),
            )
            await db.commit()

        return {
            "id": scenario_id,
            "name": name,
            "chat_history": chat_history,
            "calc_results": calc_results,
            "created_at": created_at,
        }

    async def get(self, scenario_id: str) -> dict | None:
        await self._init_db()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT id, name, chat_history, calc_results, created_at FROM scenarios WHERE id = ?",
                (scenario_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "name": row[1],
                    "chat_history": json.loads(row[2]),
                    "calc_results": json.loads(row[3]),
                    "created_at": row[4],
                }

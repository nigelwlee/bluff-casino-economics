from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import ScenarioSaveRequest, ScenarioResponse
from app.storage.sqlite_store import ScenarioStore

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

store = ScenarioStore()


@router.post("", response_model=ScenarioResponse)
async def save_scenario(req: ScenarioSaveRequest):
    scenario = await store.save(
        name=req.name,
        chat_history=[m.model_dump() for m in req.chat_history],
        calc_results=req.calc_results,
    )
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    scenario = await store.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

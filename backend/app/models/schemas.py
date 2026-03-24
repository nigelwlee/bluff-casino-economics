from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


# ─── VIP Calculator Schemas ─────────────────────────────────────────────────


class WagerMixItem(BaseModel):
    category: str
    share: float = Field(ge=0, le=1)
    rtp: float = Field(ge=0, le=1)
    edge: float = Field(ge=0, le=1)
    adj_factor: float = Field(ge=0)


class VIPCalcRequest(BaseModel):
    tier: str | None = None
    nominal_volume: float | None = None
    wager_mix: list[WagerMixItem] | None = None
    assumptions: dict[str, Any] | None = None


class VIPCompareRequest(BaseModel):
    tier: str | None = None
    nominal_volume: float | None = None
    wager_mix: list[WagerMixItem] | None = None
    scenario_a: dict[str, Any] | None = None
    scenario_b: dict[str, Any] | None = None
    scenario_a_name: str = "Current Deal"
    scenario_b_name: str = "Proposed Deal"


# ─── Company P&L Schemas ────────────────────────────────────────────────────


class CompanyPLRequest(BaseModel):
    monthly_wagers: list[float] | None = None
    starting_wagers: float = 50_000_000
    num_months: int = Field(default=12, ge=1, le=60)
    growth_rate: float | None = None
    overrides: dict[str, Any] | None = None


class VIPCompanyImpactRequest(BaseModel):
    vip_monthly_wagers: float
    vip_pct_of_total: float = Field(default=0.70, ge=0, le=1)
    vip_bonus_pct: float = Field(default=0.55, ge=0, le=1)
    non_vip_bonus_pct: float = Field(default=0.292, ge=0, le=1)
    num_months: int = Field(default=12, ge=1, le=60)
    growth_rate: float | None = None
    overrides: dict[str, Any] | None = None


class BreakevenRequest(BaseModel):
    vip_pct_of_total: float = Field(default=0.10, ge=0, le=1)
    vip_bonus_pct: float = Field(default=0.55, ge=0, le=1)
    non_vip_bonus_pct: float = Field(default=0.292, ge=0, le=1)
    overrides: dict[str, Any] | None = None


# ─── Effective Bonus Schemas ─────────────────────────────────────────────────


class EffectiveBonusRequest(BaseModel):
    total_wager_volume: float = 100_000_000
    effective_ggr_rate: float = 0.0422
    scenario: int = Field(default=3, ge=1, le=3)
    custom_distribution: list[float] | None = None


# ─── Chat Schemas ────────────────────────────────────────────────────────────


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)
    scenario_id: str | None = None


# ─── Scenario Schemas ───────────────────────────────────────────────────────


class ScenarioSaveRequest(BaseModel):
    name: str = "Untitled Scenario"
    chat_history: list[ChatMessage] = Field(default_factory=list)
    calc_results: list[dict[str, Any]] = Field(default_factory=list)


class ScenarioResponse(BaseModel):
    id: str
    name: str
    chat_history: list[ChatMessage]
    calc_results: list[dict[str, Any]]
    created_at: str

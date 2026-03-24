from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import (
    VIPCalcRequest,
    VIPCompareRequest,
    CompanyPLRequest,
    VIPCompanyImpactRequest,
    EffectiveBonusRequest,
    BreakevenRequest,
)
from app.engine.vip_calculator import calculate_vip_pl, compare_vip_pl
from app.engine.company_pl import (
    calculate_company_pl_projection,
    calculate_vip_company_impact,
    find_breakeven_volume,
)
from app.engine.effective_bonus import calculate_effective_bonus

router = APIRouter(prefix="/api/calc", tags=["calculator"])


@router.post("/vip")
async def calc_vip(req: VIPCalcRequest):
    wager_mix = [m.model_dump() for m in req.wager_mix] if req.wager_mix else None
    return calculate_vip_pl(
        tier=req.tier,
        nominal_volume=req.nominal_volume,
        wager_mix=wager_mix,
        assumptions=req.assumptions,
    )


@router.post("/vip/compare")
async def calc_vip_compare(req: VIPCompareRequest):
    wager_mix = [m.model_dump() for m in req.wager_mix] if req.wager_mix else None
    return compare_vip_pl(
        tier=req.tier,
        nominal_volume=req.nominal_volume,
        wager_mix=wager_mix,
        scenario_a=req.scenario_a,
        scenario_b=req.scenario_b,
        scenario_a_name=req.scenario_a_name,
        scenario_b_name=req.scenario_b_name,
    )


@router.post("/company-pl")
async def calc_company_pl(req: CompanyPLRequest):
    return calculate_company_pl_projection(
        monthly_wagers=req.monthly_wagers,
        starting_wagers=req.starting_wagers,
        num_months=req.num_months,
        growth_rate=req.growth_rate,
        overrides=req.overrides,
    )


@router.post("/company-pl/vip-impact")
async def calc_vip_impact(req: VIPCompanyImpactRequest):
    return calculate_vip_company_impact(
        vip_monthly_wagers=req.vip_monthly_wagers,
        vip_pct_of_total=req.vip_pct_of_total,
        vip_bonus_pct=req.vip_bonus_pct,
        non_vip_bonus_pct=req.non_vip_bonus_pct,
        num_months=req.num_months,
        growth_rate=req.growth_rate,
        overrides=req.overrides,
    )


@router.post("/company-pl/breakeven")
async def calc_breakeven(req: BreakevenRequest):
    return find_breakeven_volume(
        vip_pct_of_total=req.vip_pct_of_total,
        vip_bonus_pct=req.vip_bonus_pct,
        non_vip_bonus_pct=req.non_vip_bonus_pct,
        overrides=req.overrides,
    )


@router.post("/effective-bonus")
async def calc_effective_bonus(req: EffectiveBonusRequest):
    return calculate_effective_bonus(
        total_wager_volume=req.total_wager_volume,
        effective_ggr_rate=req.effective_ggr_rate,
        scenario=req.scenario,
        custom_distribution=req.custom_distribution,
    )

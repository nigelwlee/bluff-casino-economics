from __future__ import annotations

"""
60-Month Company-Level P&L (Model 2).
Replicates the "Monthly Model" sheet from Bluff P&L.xlsx.

Takes monthly wager inputs and projects GGR, costs, NGR, and profit
across casino (providers + OGs) and sportsbook channels.
"""

from .constants import COMPANY_PL_DEFAULTS, MONTHLY_OPEX
from .ops_cost import (
    calculate_pragmatic_cost,
    calculate_evo_cost,
    calculate_sportsbook_cost,
)


def calculate_company_pl_month(
    total_wagers: float,
    month: int = 1,
    overrides: dict | None = None,
) -> dict:
    """
    Calculate a single month's company P&L.

    Args:
        total_wagers: Total wager volume for the month.
        month: Month number (affects bonus phase).
        overrides: Override any COMPANY_PL_DEFAULTS value.

    Returns:
        Dict with full P&L breakdown for the month.
    """
    c = {**COMPANY_PL_DEFAULTS}
    if overrides:
        c.update(overrides)

    # ─── Wager split ────────────────────────────────────────────────
    casino_wagers = total_wagers * c["casino_pct"]
    sportsbook_wagers = total_wagers * c["sportsbook_pct"]

    provider_wagers = casino_wagers * c["providers_pct"]
    og_wagers = casino_wagers * c["ogs_pct"]

    pragmatic_wagers = provider_wagers * c["pragmatic_pct"]
    evo_wagers = provider_wagers * c["evo_pct"]

    # ─── GGR by channel ────────────────────────────────────────────
    pragmatic_ggr = pragmatic_wagers * (1 - c["provider_rtp"])
    evo_ggr = evo_wagers * (1 - c["provider_rtp"])
    og_ggr = og_wagers * (1 - c["og_rtp"])
    sportsbook_ggr = sportsbook_wagers * (1 - c["sportsbook_rtp"])

    casino_ggr = pragmatic_ggr + evo_ggr + og_ggr
    total_ggr = casino_ggr + sportsbook_ggr

    # ─── Bonus phase (% of GGR) ────────────────────────────────────
    if month <= 4:
        bonus_pct = c.get("bonus_pct_phase_1", 0.292)
    elif month <= 8:
        bonus_pct = c.get("bonus_pct_phase_2", 0.312)
    else:
        bonus_pct = c.get("bonus_pct_phase_3", 0.378)

    # Allow override
    if "bonus_pct" in c:
        bonus_pct = c["bonus_pct"]

    bonuses = -(total_ggr * bonus_pct)

    # ─── Ops costs ──────────────────────────────────────────────────
    use_negotiated = c.get("use_negotiated_rates", True)

    pragmatic_ops = calculate_pragmatic_cost(pragmatic_ggr, use_negotiated)
    evo_ops = calculate_evo_cost(evo_ggr, use_negotiated)
    sportsbook_ops = calculate_sportsbook_cost(sportsbook_ggr)

    casino_ops_total = -(pragmatic_ops["total_cost"] + evo_ops["total_cost"])
    sportsbook_ops_total = -(sportsbook_ops["total_cost"])

    # ─── NGR ────────────────────────────────────────────────────────
    ngr = total_ggr + bonuses + casino_ops_total + sportsbook_ops_total

    # ─── Channel costs (affiliate + referral) ───────────────────────
    affiliate_vol_pct = c.get("affiliate_channel_pct", 0.50)
    referral_vol_pct = c.get("referral_channel_pct", 0.05)
    affiliate_ngr_pct = c.get("affiliate_commission_pct", 0.30)
    referral_ngr_pct = c.get("referral_commission_pct", 0.22)

    affiliate_cost = -(ngr * affiliate_vol_pct * affiliate_ngr_pct)
    referral_cost = -(ngr * referral_vol_pct * referral_ngr_pct)

    profit_before_opex = ngr + affiliate_cost + referral_cost

    # ─── Fixed OPEX ─────────────────────────────────────────────────
    opex_overrides = c.get("opex_overrides", {})
    if "total_opex" in opex_overrides:
        # Allow overriding the total OPEX directly
        opex = {"total_opex": opex_overrides["total_opex"]}
    else:
        opex = {**MONTHLY_OPEX}
        opex.update(opex_overrides)
    total_opex = -sum(opex.values())

    profit_after_opex = profit_before_opex + total_opex

    return {
        "month": month,
        "total_wagers": total_wagers,
        "casino_wagers": casino_wagers,
        "sportsbook_wagers": sportsbook_wagers,
        "ggr": {
            "pragmatic": pragmatic_ggr,
            "evo": evo_ggr,
            "ogs": og_ggr,
            "sportsbook": sportsbook_ggr,
            "casino_total": casino_ggr,
            "total": total_ggr,
        },
        "effective_ggr_pct": total_ggr / total_wagers if total_wagers else 0,
        "bonuses": bonuses,
        "bonus_pct": bonus_pct,
        "ops_costs": {
            "pragmatic": {
                "cost": -pragmatic_ops["total_cost"],
                "effective_rate": pragmatic_ops["effective_rate"],
            },
            "evo": {
                "cost": -evo_ops["total_cost"],
                "effective_rate": evo_ops["effective_rate"],
            },
            "sportsbook": {
                "cost": -sportsbook_ops["total_cost"],
                "effective_rate": sportsbook_ops["effective_rate"],
            },
            "casino_total": casino_ops_total,
            "sportsbook_total": sportsbook_ops_total,
            "total": casino_ops_total + sportsbook_ops_total,
        },
        "ngr": ngr,
        "ngr_pct_ggr": ngr / total_ggr if total_ggr else 0,
        "channel_costs": {
            "affiliate": affiliate_cost,
            "referral": referral_cost,
            "total": affiliate_cost + referral_cost,
        },
        "profit_before_opex": profit_before_opex,
        "profit_before_opex_pct_ggr": profit_before_opex / total_ggr if total_ggr else 0,
        "opex": total_opex,
        "opex_breakdown": {k: -v for k, v in opex.items()},
        "profit_after_opex": profit_after_opex,
        "profit_after_opex_pct_ggr": profit_after_opex / total_ggr if total_ggr else 0,
    }


def calculate_company_pl_projection(
    monthly_wagers: list[float] | None = None,
    starting_wagers: float = 50_000_000,
    num_months: int = 12,
    growth_rate: float | None = None,
    overrides: dict | None = None,
) -> dict:
    """
    Multi-month projection.

    Args:
        monthly_wagers: Explicit list of monthly wager volumes.
        starting_wagers: Starting monthly wager volume (used if monthly_wagers not provided).
        num_months: Number of months to project.
        growth_rate: Monthly growth rate (e.g., 0.20 for 20%). Applied if monthly_wagers not provided.
        overrides: Override any COMPANY_PL_DEFAULTS value.

    Returns:
        Dict with monthly P&L array and cumulative totals.
    """
    if monthly_wagers is None:
        if growth_rate is not None:
            monthly_wagers = [starting_wagers * ((1 + growth_rate) ** i) for i in range(num_months)]
        else:
            monthly_wagers = [starting_wagers] * num_months

    months = []
    cumulative_wagers = 0.0
    cumulative_ggr = 0.0
    cumulative_ngr = 0.0
    cumulative_profit = 0.0
    breakeven_month = None

    for i, wagers in enumerate(monthly_wagers):
        month_num = i + 1
        result = calculate_company_pl_month(wagers, month=month_num, overrides=overrides)
        months.append(result)

        cumulative_wagers += wagers
        cumulative_ggr += result["ggr"]["total"]
        cumulative_ngr += result["ngr"]
        cumulative_profit += result["profit_after_opex"]

        if breakeven_month is None and cumulative_profit > 0:
            breakeven_month = month_num

    return {
        "months": months,
        "num_months": len(monthly_wagers),
        "cumulative": {
            "wagers": cumulative_wagers,
            "ggr": cumulative_ggr,
            "ngr": cumulative_ngr,
            "profit_after_opex": cumulative_profit,
        },
        "breakeven_month": breakeven_month,
        "summary": {
            "avg_monthly_wagers": cumulative_wagers / len(monthly_wagers),
            "avg_monthly_ggr": cumulative_ggr / len(monthly_wagers),
            "avg_ngr_margin": cumulative_ngr / cumulative_ggr if cumulative_ggr else 0,
        },
    }


def calculate_vip_company_impact(
    vip_monthly_wagers: float,
    vip_pct_of_total: float = 0.70,
    vip_bonus_pct: float = 0.55,
    non_vip_bonus_pct: float = 0.292,
    num_months: int = 12,
    growth_rate: float | None = None,
    overrides: dict | None = None,
) -> dict:
    """
    Bridge a VIP deal into the company P&L.

    Calculates blended bonus rate based on VIP vs non-VIP mix,
    then runs the company projection with that rate.

    Args:
        vip_monthly_wagers: Monthly VIP wager volume.
        vip_pct_of_total: What % of total volume is VIP.
        vip_bonus_pct: Effective bonus rate for VIP players (% of GGR).
        non_vip_bonus_pct: Bonus rate for non-VIP players.
        num_months: Projection length.
        growth_rate: Monthly growth rate.
        overrides: Additional overrides.
    """
    total_monthly_wagers = vip_monthly_wagers / vip_pct_of_total if vip_pct_of_total > 0 else vip_monthly_wagers
    non_vip_pct = 1 - vip_pct_of_total

    blended_bonus_pct = (vip_pct_of_total * vip_bonus_pct) + (non_vip_pct * non_vip_bonus_pct)

    projection_overrides = {**(overrides or {}), "bonus_pct": blended_bonus_pct}

    projection = calculate_company_pl_projection(
        starting_wagers=total_monthly_wagers,
        num_months=num_months,
        growth_rate=growth_rate,
        overrides=projection_overrides,
    )

    return {
        "vip_monthly_wagers": vip_monthly_wagers,
        "total_monthly_wagers": total_monthly_wagers,
        "vip_pct_of_total": vip_pct_of_total,
        "vip_bonus_pct": vip_bonus_pct,
        "non_vip_bonus_pct": non_vip_bonus_pct,
        "blended_bonus_pct": blended_bonus_pct,
        "projection": projection,
    }

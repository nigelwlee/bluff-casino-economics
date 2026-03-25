from __future__ import annotations

"""
VIP Player P&L Calculator (Model 1).
Replicates the "VIP P&L" sheet from Claude ver - Bluff VIP Model.xlsx.

Formula chain:
  Nominal Volume → Weighted Volume → RTP → GGR
  → Casino/Sportsbook GGR split
  → Ops Costs → Bonuses → NGR before promos
  → Affiliate costs → NGR after affiliate
  → Promos (reload, transfer, deposit match, wager milestone)
  → Final NGR
"""

from .constants import TIERS, DEFAULT_WAGER_MIX, DEFAULT_PROMO_ASSUMPTIONS


def calculate_wager_mix(nominal_volume: float, wager_mix: list[dict] | None = None) -> dict:
    """
    Step 1: Break nominal volume into categories and calculate per-category GGR.

    Each category has: share, rtp, edge, adj_factor.
    Weighted volume = nominal * share * adj_factor
    GGR per category = nominal * share * edge
    """
    mix = wager_mix or DEFAULT_WAGER_MIX
    categories = []
    total_ggr = 0.0
    total_weighted = 0.0
    casino_ggr = 0.0
    sportsbook_ggr = 0.0

    for cat in mix:
        cat_nominal = nominal_volume * cat["share"]
        cat_rtp = -(cat_nominal * cat["rtp"])
        cat_ggr = cat_nominal * cat["edge"]
        cat_weighted = cat_nominal * cat["adj_factor"]

        categories.append({
            "category": cat["category"],
            "share": cat["share"],
            "nominal": cat_nominal,
            "rtp": cat_rtp,
            "ggr": cat_ggr,
            "weighted_volume": cat_weighted,
        })

        total_ggr += cat_ggr
        total_weighted += cat_weighted

        if cat["category"] == "sportsbook":
            sportsbook_ggr += cat_ggr
        else:
            casino_ggr += cat_ggr

    return {
        "nominal_volume": nominal_volume,
        "weighted_volume": total_weighted,
        "external_volume": total_weighted * 10,
        "total_ggr": total_ggr,
        "casino_ggr": casino_ggr,
        "sportsbook_ggr": sportsbook_ggr,
        "categories": categories,
    }


def calculate_vip_pl(
    tier: str | None = None,
    nominal_volume: float | None = None,
    wager_mix: list[dict] | None = None,
    assumptions: dict | None = None,
) -> dict:
    """
    Full VIP Player P&L calculation.

    Args:
        tier: One of "whale", "dolphin", "tuna", "bass", "sardine".
              If provided, uses that tier's default nominal volume.
        nominal_volume: Override nominal volume (takes precedence over tier).
        wager_mix: Override wager mix categories.
        assumptions: Override promo/cost assumptions (merged with defaults).

    Returns:
        Complete P&L breakdown dict.
    """
    # Resolve nominal volume
    if nominal_volume is None:
        if tier and tier.lower() in TIERS:
            nominal_volume = TIERS[tier.lower()]["nominal_volume"]
        else:
            raise ValueError(f"Must provide tier or nominal_volume. Valid tiers: {list(TIERS.keys())}")

    # Merge assumptions with defaults
    a = {**DEFAULT_PROMO_ASSUMPTIONS}
    if assumptions:
        a.update(assumptions)

    # Step 1: Wager mix breakdown
    mix_result = calculate_wager_mix(nominal_volume, wager_mix)
    ggr = mix_result["total_ggr"]
    casino_ggr = mix_result["casino_ggr"]
    sportsbook_ggr = mix_result["sportsbook_ggr"]

    # Step 2: Ops costs (% of respective GGR)
    casino_ops = -(a["casino_ops_pct"] * casino_ggr)
    sportsbook_ops = -(a["sportsbook_ops_pct"] * sportsbook_ggr)
    total_ops = casino_ops + sportsbook_ops

    # Step 3: Bonuses (% of total GGR)
    level_up = -(a["level_up_pct"] * ggr)
    reload = -(a["reload_pct"] * ggr)
    weekly = -(a["weekly_pct"] * ggr)
    monthly = -(a["monthly_pct"] * ggr)
    lossback_standard = -(a["lossback_standard_pct"] * ggr)
    lossback_discretionary = -(a["lossback_discretionary_pct"] * ggr)
    total_bonuses = level_up + reload + weekly + monthly + lossback_standard + lossback_discretionary

    # Step 4: NGR before promos
    ngr_before_promos = ggr + total_ops + total_bonuses

    # Step 5: Affiliate/referral cost (% of NGR before promos)
    affiliate_cost = -(a["affiliate_pct"] * ngr_before_promos)

    # Step 6: NGR after affiliate
    ngr_after_affiliate = ngr_before_promos + affiliate_cost

    # Step 7: Additional promos
    # Reload promo (daily amount * days)
    reload_promo = 0.0
    reload_per_day = a.get("reload_promo_per_day", 0.0)
    reload_days = a.get("reload_promo_days", 7)
    if reload_per_day > 0:
        reload_promo = -(reload_per_day * reload_days)

    # Transfer promo (exponential decay, typically not active)
    transfer_promo = 0.0

    # Deposit match (proper economics with rollover recoup)
    deposit_match = 0.0
    deposit_match_detail = None
    if a.get("deposit_match_enabled"):
        dm_deposit = a.get("deposit_match_deposit", 0.0)
        dm_bonus_pct = a.get("deposit_match_bonus_pct", 1.0)
        dm_max_bonus = a.get("deposit_match_max_bonus", 0.0)
        dm_wager_req = a.get("deposit_match_wager_req", 20.0)
        dm_house_edge = a.get("deposit_match_house_edge", 0.02)
        dm_max_bet = a.get("deposit_match_max_bet", 0.0)
        dm_max_win_mult = a.get("deposit_match_max_win_mult", 0.0)

        raw_bonus = dm_deposit * dm_bonus_pct
        if dm_max_bonus > 0:
            raw_bonus = min(raw_bonus, dm_max_bonus)
        house_recoup = raw_bonus * dm_wager_req * dm_house_edge
        effective_cost = max(0.0, raw_bonus - house_recoup)
        deposit_match = -effective_cost

        deposit_match_detail = {
            "deposit": dm_deposit,
            "bonus_pct": dm_bonus_pct,
            "raw_bonus": raw_bonus,
            "house_recoup": house_recoup,
            "effective_cost": effective_cost,
            "max_bet": dm_max_bet,
            "max_win_mult": dm_max_win_mult,
        }

    # Wager milestone
    wager_milestone = 0.0
    milestone_target = a.get("wager_milestone_target", 500_000)
    milestone_type = a.get("wager_milestone_type", "Nominal")
    milestone_reward_pct = a.get("wager_milestone_reward_pct", 0.0)
    check_volume = nominal_volume if milestone_type == "Nominal" else mix_result["weighted_volume"]
    if milestone_reward_pct > 0 and check_volume >= milestone_target:
        wager_milestone = -(ggr * milestone_reward_pct)

    total_promos = reload_promo + transfer_promo + deposit_match + wager_milestone

    # Step 8: Final NGR
    ngr_after_promos = ngr_after_affiliate + total_promos

    return {
        "tier": tier,
        "nominal_volume": nominal_volume,
        "weighted_volume": mix_result["weighted_volume"],
        "external_volume": mix_result["external_volume"],
        "wager_mix": mix_result["categories"],
        "ggr": ggr,
        "casino_ggr": casino_ggr,
        "sportsbook_ggr": sportsbook_ggr,
        "ops_costs": {
            "casino_ops": casino_ops,
            "sportsbook_ops": sportsbook_ops,
            "total": total_ops,
        },
        "bonuses": {
            "level_up": level_up,
            "reload": reload,
            "weekly": weekly,
            "monthly": monthly,
            "lossback_standard": lossback_standard,
            "lossback_discretionary": lossback_discretionary,
            "total": total_bonuses,
        },
        "ngr_before_promos": ngr_before_promos,
        "affiliate_cost": affiliate_cost,
        "ngr_after_affiliate": ngr_after_affiliate,
        "promos": {
            "reload_promo": reload_promo,
            "transfer_promo": transfer_promo,
            "deposit_match": deposit_match,
            "deposit_match_detail": deposit_match_detail,
            "wager_milestone": wager_milestone,
            "total": total_promos,
        },
        "ngr_after_promos": ngr_after_promos,
        "margins": {
            "ggr_pct_of_nominal": ggr / nominal_volume if nominal_volume else 0,
            "ngr_pct_of_ggr": ngr_after_promos / ggr if ggr else 0,
            "total_cost_pct_of_ggr": (ggr - ngr_after_promos) / ggr if ggr else 0,
        },
        "assumptions_used": a,
    }


def compare_vip_pl(
    tier: str | None = None,
    nominal_volume: float | None = None,
    wager_mix: list[dict] | None = None,
    scenario_a: dict | None = None,
    scenario_b: dict | None = None,
    scenario_a_name: str = "Scenario A",
    scenario_b_name: str = "Scenario B",
) -> dict:
    """
    Compare two sets of assumptions for the same tier/volume.
    Returns both results plus a delta summary.
    """
    result_a = calculate_vip_pl(tier=tier, nominal_volume=nominal_volume,
                                 wager_mix=wager_mix, assumptions=scenario_a)
    result_b = calculate_vip_pl(tier=tier, nominal_volume=nominal_volume,
                                 wager_mix=wager_mix, assumptions=scenario_b)

    delta = {
        "ggr": result_b["ggr"] - result_a["ggr"],
        "total_bonuses": result_b["bonuses"]["total"] - result_a["bonuses"]["total"],
        "total_ops": result_b["ops_costs"]["total"] - result_a["ops_costs"]["total"],
        "ngr_before_promos": result_b["ngr_before_promos"] - result_a["ngr_before_promos"],
        "ngr_after_affiliate": result_b["ngr_after_affiliate"] - result_a["ngr_after_affiliate"],
        "ngr_after_promos": result_b["ngr_after_promos"] - result_a["ngr_after_promos"],
    }

    return {
        scenario_a_name: result_a,
        scenario_b_name: result_b,
        "delta": delta,
    }

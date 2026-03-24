"""
Tiered provider cost calculators.
Replicates the progressive (tax-bracket-style) cost calculations from the
"Casino Provider Cost" and "Sportsbook Rev Share Schedule" sheets.
"""

from .constants import (
    CASINO_PROVIDER_TIERS,
    SPORTSBOOK_TIERS_EUR,
    EUR_TO_USD,
    PRAGMATIC_NEGOTIATED_TIERS,
    EVO_NEGOTIATED_TIERS,
    OLD_PRAGMATIC_RATE,
    OLD_EVO_RATE,
)


def calculate_tiered_cost(wagers: float, tiers: list[dict]) -> dict:
    """
    Progressive (tax-bracket) cost calculation.
    Each tier's rate only applies to the portion of wagers within that bracket.

    Returns dict with total_cost, effective_rate, and tier_breakdown.
    """
    total_cost = 0.0
    breakdown = []
    remaining = wagers

    for tier in tiers:
        if remaining <= 0:
            break
        tier_from = tier["from"]
        tier_to = tier["to"]
        rate = tier["rate"]
        bracket_size = tier_to - tier_from
        taxable = min(remaining, bracket_size) if bracket_size != float("inf") else remaining
        cost = taxable * rate
        total_cost += cost
        breakdown.append({
            "from": tier_from,
            "to": min(tier_to, tier_from + taxable),
            "rate": rate,
            "wagers_in_bracket": taxable,
            "cost": cost,
        })
        remaining -= taxable

    effective_rate = total_cost / wagers if wagers > 0 else 0.0

    return {
        "total_cost": total_cost,
        "effective_rate": effective_rate,
        "tier_breakdown": breakdown,
    }


def calculate_casino_provider_cost(wagers: float) -> dict:
    """Calculate casino provider cost using progressive tiers."""
    return calculate_tiered_cost(wagers, CASINO_PROVIDER_TIERS)


def calculate_sportsbook_cost(ggr_usd: float) -> dict:
    """
    Calculate sportsbook provider cost.
    Tiers are EUR-based, so convert GGR to EUR first, apply tiers, result is in USD.
    """
    ggr_eur = ggr_usd / EUR_TO_USD
    result = calculate_tiered_cost(ggr_eur, SPORTSBOOK_TIERS_EUR)
    # Convert costs back to USD
    return {
        "total_cost": result["total_cost"] * EUR_TO_USD,
        "effective_rate": result["effective_rate"],
        "tier_breakdown": [
            {**t, "cost": t["cost"] * EUR_TO_USD} for t in result["tier_breakdown"]
        ],
    }


def calculate_pragmatic_cost(ggr: float, use_negotiated: bool = True) -> dict:
    """Calculate Pragmatic (Slots) provider cost."""
    if use_negotiated:
        return calculate_tiered_cost(ggr, PRAGMATIC_NEGOTIATED_TIERS)
    return {
        "total_cost": ggr * OLD_PRAGMATIC_RATE,
        "effective_rate": OLD_PRAGMATIC_RATE,
        "tier_breakdown": [{"rate": OLD_PRAGMATIC_RATE, "cost": ggr * OLD_PRAGMATIC_RATE}],
    }


def calculate_evo_cost(ggr: float, use_negotiated: bool = True) -> dict:
    """Calculate Evo (Live) provider cost."""
    if use_negotiated:
        return calculate_tiered_cost(ggr, EVO_NEGOTIATED_TIERS)
    return {
        "total_cost": ggr * OLD_EVO_RATE,
        "effective_rate": OLD_EVO_RATE,
        "tier_breakdown": [{"rate": OLD_EVO_RATE, "cost": ggr * OLD_EVO_RATE}],
    }

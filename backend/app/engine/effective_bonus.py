from __future__ import annotations

"""
20-Level VIP Effective Bonus Calculator.
Replicates the "Effective Bonus Calc" sheet from Bluff P&L.xlsx.

Given a total wager volume and player distribution across 20 VIP levels,
calculates the blended effective bonus rate as a percentage of GGR.
"""

from .constants import VIP_BONUS_LEVELS


# Scenario distributions: % of players at each level (20 levels)
SCENARIO_DISTRIBUTIONS = {
    1: [  # Conservative / Early stage
        0.15, 0.10, 0.10, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04,
        0.04, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.01,
    ],
    2: [  # Moderate / Mid stage
        0.12, 0.08, 0.07, 0.07, 0.06, 0.06, 0.06, 0.05, 0.05, 0.05,
        0.04, 0.04, 0.04, 0.04, 0.03, 0.03, 0.03, 0.03, 0.03, 0.02,
    ],
    3: [  # Aggressive / Steady state
        0.02, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.05, 0.05, 0.05,
        0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.07, 0.07, 0.08, 0.10,
    ],
}


def calculate_effective_bonus(
    total_wager_volume: float = 100_000_000,
    effective_ggr_rate: float = 0.0422,
    scenario: int = 3,
    custom_distribution: list[float] | None = None,
) -> dict:
    """
    Calculate the blended effective bonus rate across 20 VIP levels.

    Args:
        total_wager_volume: Total wager volume to distribute.
        effective_ggr_rate: GGR rate used (default 4.22% from Excel).
        scenario: Distribution scenario (1=conservative, 2=moderate, 3=aggressive).
        custom_distribution: Optional list of 20 floats (must sum to 1.0).

    Returns:
        Dict with per-level breakdown and blended effective rate.
    """
    distribution = custom_distribution or SCENARIO_DISTRIBUTIONS.get(scenario)
    if distribution is None:
        raise ValueError(f"Invalid scenario: {scenario}. Use 1, 2, or 3.")
    if len(distribution) != 20:
        raise ValueError(f"Distribution must have 20 entries, got {len(distribution)}")

    total_ggr = total_wager_volume * effective_ggr_rate
    total_bonuses = 0.0
    levels_detail = []

    for i, level_def in enumerate(VIP_BONUS_LEVELS):
        pct = distribution[i]
        level_wager = total_wager_volume * pct
        level_ggr = level_wager * effective_ggr_rate

        # Use the pre-computed effective_cost_pct from the Excel model.
        # This captures all 7 bonus types + ops costs for each VIP level.
        effective_cost_pct = level_def["effective_cost_pct"]
        level_total_bonus = -(level_ggr * effective_cost_pct)
        total_bonuses += level_total_bonus

        levels_detail.append({
            "level": level_def["level"],
            "player_pct": pct,
            "wager_volume": level_wager,
            "ggr": level_ggr,
            "effective_cost_pct": effective_cost_pct,
            "total_bonus": level_total_bonus,
            "bonus_pct_of_ggr": -effective_cost_pct,
        })

    effective_bonus_pct = total_bonuses / total_ggr if total_ggr else 0

    return {
        "total_wager_volume": total_wager_volume,
        "effective_ggr_rate": effective_ggr_rate,
        "total_ggr": total_ggr,
        "total_bonuses": total_bonuses,
        "effective_bonus_pct": effective_bonus_pct,
        "scenario": scenario,
        "levels": levels_detail,
    }

"""
Tool definitions for the LLM and execution dispatch.
"""

from __future__ import annotations

from app.engine.vip_calculator import calculate_vip_pl, compare_vip_pl
from app.engine.company_pl import (
    calculate_company_pl_projection,
    calculate_vip_company_impact,
)
from app.engine.effective_bonus import calculate_effective_bonus


# ─── Tool Definitions (for LLM function calling) ───────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "calculate_vip_pl",
        "description": "Calculate the P&L for a VIP player at a specific tier or wager volume. Returns GGR, ops costs, bonuses, NGR breakdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["whale", "dolphin", "tuna", "bass", "sardine"],
                    "description": "VIP tier name. Each has a default wager volume.",
                },
                "nominal_volume": {
                    "type": "number",
                    "description": "Override the wager volume (in USD). Takes precedence over tier default.",
                },
                "assumptions": {
                    "type": "object",
                    "description": "Override default promo/cost assumptions. Keys: casino_ops_pct, sportsbook_ops_pct, affiliate_pct, level_up_pct, reload_pct, weekly_pct, monthly_pct, lossback_standard_pct, lossback_discretionary_pct, deposit_match_enabled, deposit_match_deposit, deposit_match_bonus_pct, deposit_match_max_bonus, deposit_match_wager_req, deposit_match_house_edge.",
                    "properties": {
                        "casino_ops_pct": {"type": "number"},
                        "sportsbook_ops_pct": {"type": "number"},
                        "affiliate_pct": {"type": "number"},
                        "level_up_pct": {"type": "number"},
                        "reload_pct": {"type": "number"},
                        "weekly_pct": {"type": "number"},
                        "monthly_pct": {"type": "number"},
                        "lossback_standard_pct": {"type": "number"},
                        "lossback_discretionary_pct": {"type": "number"},
                        "deposit_match_enabled": {"type": "boolean", "description": "Enable deposit match promo."},
                        "deposit_match_deposit": {"type": "number", "description": "Fixed monthly deposit amount ($)."},
                        "deposit_match_bonus_pct": {"type": "number", "description": "Match percentage (1.0 = 100%)."},
                        "deposit_match_max_bonus": {"type": "number", "description": "Cap on bonus paid (0 = no cap)."},
                        "deposit_match_wager_req": {"type": "number", "description": "Rollover multiplier (e.g. 20 = 20x)."},
                        "deposit_match_house_edge": {"type": "number", "description": "House edge during rollover (e.g. 0.02 = 2%)."},
                    },
                },
            },
        },
    },
    {
        "name": "calculate_vip_pl_comparison",
        "description": "Compare two sets of assumptions for the same VIP tier. Shows both P&Ls and the delta between them.",
        "parameters": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["whale", "dolphin", "tuna", "bass", "sardine"],
                },
                "nominal_volume": {"type": "number"},
                "scenario_a": {
                    "type": "object",
                    "description": "First scenario assumptions (defaults if not specified).",
                },
                "scenario_b": {
                    "type": "object",
                    "description": "Second scenario assumptions to compare against.",
                },
                "scenario_a_name": {"type": "string", "default": "Current Deal"},
                "scenario_b_name": {"type": "string", "default": "Proposed Deal"},
            },
        },
    },
    {
        "name": "calculate_company_pl",
        "description": "Run a multi-month company-level P&L projection. Shows wagers, GGR, costs, NGR, OPEX, and profit by month.",
        "parameters": {
            "type": "object",
            "properties": {
                "starting_wagers": {
                    "type": "number",
                    "description": "Starting monthly wager volume in USD. Default $50M.",
                    "default": 50000000,
                },
                "num_months": {
                    "type": "integer",
                    "description": "Number of months to project (1-60). Default 12.",
                    "default": 12,
                },
                "growth_rate": {
                    "type": "number",
                    "description": "Monthly growth rate as decimal (e.g., 0.20 for 20%).",
                },
                "monthly_wagers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Explicit list of monthly wager volumes (overrides starting_wagers and growth_rate).",
                },
                "overrides": {
                    "type": "object",
                    "description": "Override company P&L defaults (casino_pct, sportsbook_pct, bonus_pct, etc.).",
                },
            },
        },
    },
    {
        "name": "calculate_effective_bonus",
        "description": "Calculate the blended effective bonus rate across 20 VIP levels for a given player distribution scenario.",
        "parameters": {
            "type": "object",
            "properties": {
                "total_wager_volume": {
                    "type": "number",
                    "description": "Total wager volume to distribute. Default $100M.",
                    "default": 100000000,
                },
                "effective_ggr_rate": {
                    "type": "number",
                    "description": "GGR rate. Default 4.22%.",
                    "default": 0.0422,
                },
                "scenario": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "Player distribution scenario. 1=Conservative, 2=Moderate, 3=Aggressive (steady state).",
                    "default": 3,
                },
            },
        },
    },
    {
        "name": "calculate_vip_company_impact",
        "description": "Bridge a VIP deal into the company P&L. Shows how VIP bonus rates affect company profitability and breakeven timeline.",
        "parameters": {
            "type": "object",
            "properties": {
                "vip_monthly_wagers": {
                    "type": "number",
                    "description": "Monthly VIP wager volume in USD.",
                },
                "vip_pct_of_total": {
                    "type": "number",
                    "description": "What percentage of total volume is VIP (0-1). Default 0.70.",
                    "default": 0.70,
                },
                "vip_bonus_pct": {
                    "type": "number",
                    "description": "Effective bonus rate for VIP players as % of GGR (0-1). Default 0.55.",
                    "default": 0.55,
                },
                "non_vip_bonus_pct": {
                    "type": "number",
                    "description": "Bonus rate for non-VIP players. Default 0.292.",
                    "default": 0.292,
                },
                "vip_deposit_match_cost": {
                    "type": "number",
                    "description": "VIP deposit match effective cost to deduct from company NGR. Default 0.",
                    "default": 0,
                },
                "num_months": {
                    "type": "integer",
                    "description": "Projection length. Default 12.",
                    "default": 12,
                },
                "growth_rate": {
                    "type": "number",
                    "description": "Monthly growth rate.",
                },
            },
            "required": ["vip_monthly_wagers"],
        },
    },
]


# ─── Tool Execution Dispatch ────────────────────────────────────────────────

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool by name with the given arguments. Returns the result dict."""
    if tool_name == "calculate_vip_pl":
        return calculate_vip_pl(
            tier=arguments.get("tier"),
            nominal_volume=arguments.get("nominal_volume"),
            assumptions=arguments.get("assumptions"),
        )
    elif tool_name == "calculate_vip_pl_comparison":
        return compare_vip_pl(
            tier=arguments.get("tier"),
            nominal_volume=arguments.get("nominal_volume"),
            scenario_a=arguments.get("scenario_a"),
            scenario_b=arguments.get("scenario_b"),
            scenario_a_name=arguments.get("scenario_a_name", "Current Deal"),
            scenario_b_name=arguments.get("scenario_b_name", "Proposed Deal"),
        )
    elif tool_name == "calculate_company_pl":
        return calculate_company_pl_projection(
            monthly_wagers=arguments.get("monthly_wagers"),
            starting_wagers=arguments.get("starting_wagers", 50_000_000),
            num_months=arguments.get("num_months", 12),
            growth_rate=arguments.get("growth_rate"),
            overrides=arguments.get("overrides"),
        )
    elif tool_name == "calculate_effective_bonus":
        return calculate_effective_bonus(
            total_wager_volume=arguments.get("total_wager_volume", 100_000_000),
            effective_ggr_rate=arguments.get("effective_ggr_rate", 0.0422),
            scenario=arguments.get("scenario", 3),
            custom_distribution=arguments.get("custom_distribution"),
        )
    elif tool_name == "calculate_vip_company_impact":
        return calculate_vip_company_impact(
            vip_monthly_wagers=arguments["vip_monthly_wagers"],
            vip_pct_of_total=arguments.get("vip_pct_of_total", 0.70),
            vip_bonus_pct=arguments.get("vip_bonus_pct", 0.55),
            non_vip_bonus_pct=arguments.get("non_vip_bonus_pct", 0.292),
            vip_deposit_match_cost=arguments.get("vip_deposit_match_cost", 0.0),
            num_months=arguments.get("num_months", 12),
            growth_rate=arguments.get("growth_rate"),
            overrides=arguments.get("overrides"),
        )
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

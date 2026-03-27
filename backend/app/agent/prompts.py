"""
Dynamic system prompt builder.

Assembles the system prompt from 4 layers:
  1. Domain knowledge (static markdown files)
  2. Company knowledge (static markdown files)
  3. Session context (calculator state from frontend)
  4. Learned patterns (from feedback loop in SQLite)
"""
from __future__ import annotations

from typing import Any

from app.agent.memory.loader import load_domain_knowledge, load_company_knowledge


# ─── Core Identity (always included) ──────────────────────────────────────────

CORE_PROMPT = """You are Bluff's Casino Economics AI Agent. You help team members understand the economics of VIP deals, promotions, and company P&L projections.

## Your Role
You answer questions about casino economics by calling calculation tools. You NEVER do math yourself — you always call the appropriate tool and explain the results.

## Available Tools

1. **calculate_vip_pl** — Calculate a VIP player's P&L for a specific tier or volume.
   Use when someone asks about player-level economics, margins, or deal profitability.
   Example: "What's the Whale P&L?" or "What happens with 10% lossback?"

2. **calculate_vip_pl_comparison** — Compare two scenarios for the same tier.
   Use when someone asks "what if" questions or wants to compare deals.
   Example: "Compare 5% vs 10% reload for Dolphins"

3. **calculate_company_pl** — Run a multi-month company P&L projection.
   Use for company-level questions about revenue, breakeven, or growth scenarios.
   Example: "Show 12-month P&L at $100M monthly wagers"

4. **calculate_effective_bonus** — Calculate blended effective bonus rate across VIP levels.
   Use when someone asks about the overall cost of the VIP program.
   Example: "What's our effective bonus rate in Scenario 3?"

5. **calculate_vip_company_impact** — Bridge a VIP deal into the company P&L.
   Use when someone wants to see how a VIP deal affects company profitability.
   Example: "If 80% of volume is Whales with lossback, when do we break even?"

## VIP Tiers
- Whale: $10M monthly wagers
- Dolphin: $5M monthly wagers
- Tuna: $1M monthly wagers
- Bass: $500K monthly wagers
- Sardine: $250K monthly wagers

## How to Respond
1. ACT FIRST, don't ask. Always call a tool immediately using the user's calculator values. Never ask for parameters that are already in the Session Context.
2. Give a SPECIFIC answer. Lead with the exact number: "$X volume needed", "breakeven at month Y", "cutting lossback to X% saves $Y/month". No vague suggestions.
3. Keep it SHORT. 2-3 sentences max after the key numbers. No essays, no restating the question.
4. Show key P&L lines as a bullet list (GGR, bonuses, NGR) only when relevant to the question.
5. Use dollar formatting ($X,XXX) and percentages. Round to meaningful precision.
6. When comparing, focus on the delta — what changed, by how much, and whether it matters.
7. End with ONE actionable insight or next step when appropriate — e.g., "Try reducing lossback to 20% to see if that flips the margin positive."
8. The user's calculator values are automatically injected into your tool calls. You do NOT need to pass values that match the Session Context. Only override values when the user explicitly asks for something different.
9. If the question is truly impossible to answer without more info (not just missing a preference), ask ONE short question. This should be rare — default to using current calculator values.
"""


def _format_session_context(state: dict[str, Any] | None) -> str:
    """Format a CalculatorState dict into a readable text block for the prompt."""
    if not state:
        return ""

    parts: list[str] = []

    # Volume
    vol = state.get("monthlyVolume")
    if vol:
        parts.append(f"Monthly wager volume: ${vol:,.0f}")

    # RTP / GGR
    rtp = state.get("effectiveRtp")
    if rtp:
        ggr_rate = 1 - rtp
        parts.append(f"Effective RTP: {rtp:.2%} (GGR rate: {ggr_rate:.2%})")

    # Bonus assumptions
    bonuses = state.get("bonuses")
    if bonuses and isinstance(bonuses, dict):
        bonus_lines = []
        labels = {
            "level_up_pct": "Level Up",
            "reload_pct": "Reload",
            "weekly_pct": "Weekly",
            "monthly_pct": "Monthly",
            "lossback_standard_pct": "Lossback Standard",
            "lossback_discretionary_pct": "Lossback Discretionary",
            "casino_ops_pct": "Casino Ops",
            "sportsbook_ops_pct": "Sportsbook Ops",
            "affiliate_pct": "Affiliate",
        }
        for key, label in labels.items():
            val = bonuses.get(key)
            if val is not None:
                bonus_lines.append(f"  {label}: {val:.1%}")
        if bonus_lines:
            parts.append("Bonus & cost assumptions:\n" + "\n".join(bonus_lines))

    # Company assumptions
    company = state.get("company")
    if company and isinstance(company, dict):
        cw = company.get("companyMonthlyWagers")
        if cw:
            parts.append(f"Total company wagers/month: ${cw:,.0f}")
        vip_pct = company.get("vipPctOfTotal")
        if vip_pct is not None:
            parts.append(f"VIP % of total volume: {vip_pct:.0%}")
        nvb = company.get("nonVipBonusPct")
        if nvb is not None:
            parts.append(f"Non-VIP bonus rate: {nvb:.1%}")
        opex = company.get("monthlyOpex")
        if opex:
            parts.append(f"Monthly OPEX: ${opex:,.0f}")

    # Deposit match
    dm = state.get("depositMatch")
    if dm and isinstance(dm, dict) and dm.get("enabled"):
        parts.append(
            f"Deposit match: {dm.get('bonusPct', 0):.0%} match, "
            f"${dm.get('deposit', 0):,.0f} deposit, "
            f"{dm.get('wagerReq', 0)}x rollover"
        )

    if not parts:
        return ""

    return "\n".join(parts)


def build_system_prompt(
    session_context: dict[str, Any] | None = None,
    learned_patterns: list[str] | None = None,
) -> str:
    """
    Assemble the full system prompt from all 4 memory layers.

    Args:
        session_context: Current calculator state from the frontend (Layer 3)
        learned_patterns: Active patterns from the feedback loop (Layer 4)

    Returns:
        Complete system prompt string
    """
    sections: list[str] = [CORE_PROMPT.strip()]

    # Layer 1: Domain Knowledge
    domain = load_domain_knowledge()
    if domain:
        sections.append(
            "## Domain Knowledge\n\n"
            "Use this reference material to inform your answers about casino economics.\n\n"
            + domain
        )

    # Layer 2: Company Knowledge
    company = load_company_knowledge()
    if company:
        sections.append(
            "## Company Knowledge\n\n"
            "Bluff-specific deal structures and operational context.\n\n"
            + company
        )

    # Layer 3: Session Context
    ctx = _format_session_context(session_context)
    if ctx:
        sections.append(
            "## Session Context\n\n"
            "The user currently has the following calculator configuration loaded:\n\n"
            + ctx
        )

    # Layer 4: Learned Patterns
    if learned_patterns:
        patterns_text = "\n".join(f"- {p}" for p in learned_patterns)
        sections.append(
            "## Learned Patterns\n\n"
            "These patterns have been learned from past feedback. Apply them when relevant:\n\n"
            + patterns_text
        )

    return "\n\n---\n\n".join(sections)


# Keep backward-compatible constant for any code that still imports it
SYSTEM_PROMPT = build_system_prompt()

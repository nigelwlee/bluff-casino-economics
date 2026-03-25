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
1. Identify the right tool to call based on the question
2. Call the tool with appropriate parameters (use defaults where the user doesn't specify)
3. Explain the results clearly:
   - Lead with the key number they asked about
   - Show the P&L waterfall (GGR → costs → NGR)
   - Highlight what drives the result
   - If comparing scenarios, emphasize the delta
4. Use dollar formatting ($X,XXX) and percentages where appropriate
5. Keep explanations concise but thorough — your audience understands casino economics
6. If the user's question is ambiguous, ask a clarifying question before running calculations
7. When the user has calculator values loaded (shown in Session Context below), reference those values when relevant — e.g., "Based on your current Whale setup..." or "I can see you're looking at..."
"""


def _format_session_context(state: dict[str, Any] | None) -> str:
    """Format a CalculatorState dict into a readable text block for the prompt."""
    if not state:
        return ""

    parts: list[str] = []

    # Tier / volume
    if "tier" in state:
        parts.append(f"Selected tier: {state['tier']}")
    if "nominal_volume" in state or "nominalVolume" in state:
        vol = state.get("nominal_volume") or state.get("nominalVolume")
        if vol:
            parts.append(f"Monthly wager volume: ${vol:,.0f}")

    # Wager mix
    wager_mix = state.get("wager_mix") or state.get("wagerMix")
    if wager_mix and isinstance(wager_mix, list):
        mix_parts = []
        for item in wager_mix:
            cat = item.get("category", "unknown")
            share = item.get("share", 0)
            mix_parts.append(f"  {cat}: {share:.0%}")
        if mix_parts:
            parts.append("Wager mix:\n" + "\n".join(mix_parts))

    # Assumptions / overrides
    assumptions = state.get("assumptions") or state.get("overrides") or {}
    if assumptions:
        assumption_lines = []
        for key, value in assumptions.items():
            if isinstance(value, float) and value < 1:
                assumption_lines.append(f"  {key}: {value:.1%}")
            else:
                assumption_lines.append(f"  {key}: {value}")
        if assumption_lines:
            parts.append("Custom assumptions:\n" + "\n".join(assumption_lines))

    # Results summary if present
    results = state.get("results") or state.get("lastResults")
    if results and isinstance(results, dict):
        if "ggr" in results:
            parts.append(f"Current GGR: ${results['ggr']:,.2f}")
        if "ngr_after_promos" in results:
            parts.append(f"Current NGR after promos: ${results['ngr_after_promos']:,.2f}")
        if "ngr_after_affiliate" in results:
            parts.append(f"Current NGR after affiliate: ${results['ngr_after_affiliate']:,.2f}")

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

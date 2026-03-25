"""
All default values extracted from the two Excel models:
  - Claude ver - Bluff VIP Model.xlsx
  - Bluff P&L.xlsx
"""

# ─── VIP Player Tiers ───────────────────────────────────────────────────────

TIERS = {
    "whale":   {"nominal_volume": 10_000_000},
    "dolphin": {"nominal_volume": 5_000_000},
    "tuna":    {"nominal_volume": 1_000_000},
    "bass":    {"nominal_volume": 500_000},
    "sardine": {"nominal_volume": 250_000},
}

# ─── Default Wager Mix (VIP Model cells C13:F17) ────────────────────────────

DEFAULT_WAGER_MIX = [
    {"category": "casino_99_plus",  "share": 0.80, "rtp": 0.99,   "edge": 0.01,   "adj_factor": 0.10},
    {"category": "casino_975_99",   "share": 0.05, "rtp": 0.9825, "edge": 0.0175, "adj_factor": 0.175},
    {"category": "casino_975",      "share": 0.05, "rtp": 0.975,  "edge": 0.025,  "adj_factor": 0.25},
    {"category": "casino_sub_975",  "share": 0.05, "rtp": 0.9475, "edge": 0.0525, "adj_factor": 0.525},
    {"category": "sportsbook",      "share": 0.05, "rtp": 0.93,   "edge": 0.07,   "adj_factor": 0.70},
]

# ─── Default Promo / Cost Assumptions (VIP Model cells H6-H45) ──────────────

DEFAULT_PROMO_ASSUMPTIONS = {
    # Ops costs (% of GGR)
    "casino_ops_pct": 0.10,
    "sportsbook_ops_pct": 0.11,
    # Affiliate (% of NGR before promos)
    "affiliate_pct": 0.25,
    # Bonus rates (% of GGR)
    "level_up_pct": 0.05,
    "reload_pct": 0.10,
    "weekly_pct": 0.03,
    "monthly_pct": 0.07,
    "lossback_standard_pct": 0.30,
    "lossback_discretionary_pct": 0.00,
    # Deposit match promo
    "deposit_match_enabled": False,
    "deposit_match_deposit": 0.0,        # Fixed monthly deposit amount ($)
    "deposit_match_bonus_pct": 1.0,      # Match percentage (1.0 = 100%)
    "deposit_match_max_bonus": 0.0,      # Cap on bonus paid (0 = no cap)
    "deposit_match_wager_req": 20.0,     # Rollover multiplier (Xx)
    "deposit_match_house_edge": 0.02,    # House edge during rollover
    "deposit_match_max_bet": 0.0,        # Max bet during rollover (metadata)
    "deposit_match_max_win_mult": 0.0,   # Max win multiplier (metadata)
    # Wager milestone promo
    "wager_milestone_target": 500_000,
    "wager_milestone_type": "Nominal",  # "Nominal" or "Weighted"
    "wager_milestone_reward_pct": 0.0,
}

# ─── Company P&L Defaults (Bluff P&L - Monthly Model) ───────────────────────

COMPANY_PL_DEFAULTS = {
    # Wager split
    "casino_pct": 0.92,
    "sportsbook_pct": 0.08,
    # Casino sub-split (within casino wagers)
    "providers_pct": 0.50,      # 50% of casino goes through providers
    "ogs_pct": 0.50,            # 50% through OGs
    # Provider sub-split (within provider wagers)
    "pragmatic_pct": 0.40,      # 40% Pragmatic (Slots)
    "evo_pct": 0.60,            # 60% Evo (Live)
    # RTP by channel
    "casino_rtp": 0.98,         # Providers: 97%, but "casino" blended is 98%
    "provider_rtp": 0.97,
    "og_rtp": 0.99,
    "sportsbook_rtp": 0.92,
    # Effective GGR rate (blended)
    "effective_ggr_pct": 0.0248,
    # Channel acquisition mix (% of wagers from each channel)
    "affiliate_channel_pct": 0.50,
    "referral_channel_pct": 0.05,
    "paid_channel_pct": 0.40,
    "brand_channel_pct": 0.05,
    # Channel commission rates (% of NGR paid)
    "affiliate_commission_pct": 0.30,
    "referral_commission_pct": 0.22,
    # Bonus % of GGR (varies by growth phase)
    "bonus_pct_phase_1": 0.292,   # Months 1-4
    "bonus_pct_phase_2": 0.312,   # Months 5-8
    "bonus_pct_phase_3": 0.378,   # Months 9+
    # Ops cost rates (% of GGR for that segment)
    "pragmatic_ops_pct": 0.065,   # New negotiated: 6.5% flat (simplified)
    "evo_ops_pct": 0.075,         # New negotiated: ~7.5% effective
    "sportsbook_ops_base_pct": 0.11,  # Starting rate (tiered)
}

# ─── Casino Provider Cost Tiers (Progressive method) ────────────────────────

CASINO_PROVIDER_TIERS = [
    {"from": 0,          "to": 5_000_000,   "rate": 0.09},
    {"from": 5_000_000,  "to": 10_000_000,  "rate": 0.085},
    {"from": 10_000_000, "to": 15_000_000,  "rate": 0.08},
    {"from": 15_000_000, "to": 20_000_000,  "rate": 0.075},
    {"from": 20_000_000, "to": 25_000_000,  "rate": 0.07},
    {"from": 25_000_000, "to": 30_000_000,  "rate": 0.065},
    {"from": 30_000_000, "to": float("inf"), "rate": 0.065},
]

# ─── Sportsbook Cost Tiers (EUR-based, converted to USD) ────────────────────

EUR_TO_USD = 1.15

SPORTSBOOK_TIERS_EUR = [
    {"from": 0,           "to": 500_000,    "rate": 0.11},
    {"from": 500_000,     "to": 1_000_000,  "rate": 0.10},
    {"from": 1_000_000,   "to": 2_000_000,  "rate": 0.09},
    {"from": 2_000_000,   "to": 3_000_000,  "rate": 0.08},
    {"from": 3_000_000,   "to": 4_000_000,  "rate": 0.07},
    {"from": 4_000_000,   "to": 5_000_000,  "rate": 0.06},
    {"from": 5_000_000,   "to": 7_500_000,  "rate": 0.055},
    {"from": 7_500_000,   "to": float("inf"), "rate": 0.05},
]

# ─── Pragmatic Negotiated Tiers (new deal via Mo) ───────────────────────────

PRAGMATIC_NEGOTIATED_TIERS = [
    {"from": 0,          "to": 20_000_000,   "rate": 0.065},
    {"from": 20_000_000, "to": float("inf"), "rate": 0.06},
]

# ─── Evo Negotiated Tiers (new deal via Mo) ─────────────────────────────────

EVO_NEGOTIATED_TIERS = [
    {"from": 0,          "to": 5_000_000,   "rate": 0.09},
    {"from": 5_000_000,  "to": 10_000_000,  "rate": 0.085},
    {"from": 10_000_000, "to": 15_000_000,  "rate": 0.08},
    {"from": 15_000_000, "to": 20_000_000,  "rate": 0.075},
    {"from": 20_000_000, "to": 25_000_000,  "rate": 0.07},
    {"from": 25_000_000, "to": 30_000_000,  "rate": 0.065},
]

# ─── "Old" Provider Rates (own negotiation, flat 10%) ───────────────────────

OLD_PRAGMATIC_RATE = 0.10
OLD_EVO_RATE = 0.10

# ─── 20-Level VIP Bonus Structure ───────────────────────────────────────────
# Extracted from VIP Model "Bonus Calculator" sheet (rows 48-67)
# Each level has: wager_threshold, ggr, deposit, rakeback (0 for all),
# level_up, reload, monthly bonuses, and various percentages

VIP_BONUS_LEVELS = [
    {"level": 1,  "wager_threshold": 1_000_000,    "ggr": 30_000,     "deposit": 300,
     "level_up": 0,       "reload": 1215,    "monthly": 2294,    "total_bonus": 3088,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2128},
    {"level": 2,  "wager_threshold": 2_000_000,    "ggr": 60_000,     "deposit": 600,
     "level_up": 250,     "reload": 2430,    "monthly": 4588,    "total_bonus": 6376,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2170},
    {"level": 3,  "wager_threshold": 3_000_000,    "ggr": 90_000,     "deposit": 1_000,
     "level_up": 500,     "reload": 3645,    "monthly": 6882,    "total_bonus": 9564,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2239},
    {"level": 4,  "wager_threshold": 5_000_000,    "ggr": 150_000,    "deposit": 2_000,
     "level_up": 1_000,   "reload": 6075,    "monthly": 11470,   "total_bonus": 15440,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2128},
    {"level": 5,  "wager_threshold": 7_500_000,    "ggr": 225_000,    "deposit": 3_000,
     "level_up": 1_500,   "reload": 9112,    "monthly": 17205,   "total_bonus": 23160,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2128},
    {"level": 6,  "wager_threshold": 10_000_000,   "ggr": 300_000,    "deposit": 5_000,
     "level_up": 2_000,   "reload": 12150,   "monthly": 22940,   "total_bonus": 30880,
     "bonus_pct_ggr": 0.01667, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2161},
    {"level": 7,  "wager_threshold": 12_500_000,   "ggr": 375_000,    "deposit": 7_500,
     "level_up": 3_000,   "reload": 15188,   "monthly": 28675,   "total_bonus": 38600,
     "bonus_pct_ggr": 0.02, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2228},
    {"level": 8,  "wager_threshold": 15_000_000,   "ggr": 450_000,    "deposit": 10_000,
     "level_up": 4_000,   "reload": 18225,   "monthly": 34410,   "total_bonus": 46320,
     "bonus_pct_ggr": 0.02222, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2261},
    {"level": 9,  "wager_threshold": 17_500_000,   "ggr": 525_000,    "deposit": 12_000,
     "level_up": 5_000,   "reload": 21263,   "monthly": 40145,   "total_bonus": 54040,
     "bonus_pct_ggr": 0.02286, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.0,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2268},
    {"level": 10, "wager_threshold": 20_000_000,   "ggr": 600_000,    "deposit": 15_000,
     "level_up": 7_500,   "reload": 24300,   "monthly": 45880,   "total_bonus": 61760,
     "bonus_pct_ggr": 0.025, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.05,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2828},
    {"level": 11, "wager_threshold": 25_000_000,   "ggr": 750_000,    "deposit": 20_000,
     "level_up": 10_000,  "reload": 30375,   "monthly": 57350,   "total_bonus": 77200,
     "bonus_pct_ggr": 0.02667, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.05,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2839},
    {"level": 12, "wager_threshold": 30_000_000,   "ggr": 900_000,    "deposit": 25_000,
     "level_up": 15_000,  "reload": 36450,   "monthly": 68820,   "total_bonus": 92640,
     "bonus_pct_ggr": 0.02778, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.05,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2861},
    {"level": 13, "wager_threshold": 40_000_000,   "ggr": 1_200_000,  "deposit": 30_000,
     "level_up": 20_000,  "reload": 48600,   "monthly": 91760,   "total_bonus": 123520,
     "bonus_pct_ggr": 0.025, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.05,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2828},
    {"level": 14, "wager_threshold": 50_000_000,   "ggr": 1_500_000,  "deposit": 35_000,
     "level_up": 25_000,  "reload": 60750,   "monthly": 114700,  "total_bonus": 154400,
     "bonus_pct_ggr": 0.02333, "reload_pct_ggr": 0.0405,
     "lossback_pct": 0.0, "cashback_pct": 0.05,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.2811},
    {"level": 15, "wager_threshold": 60_000_000,   "ggr": 1_800_000,  "deposit": 40_000,
     "level_up": 0,       "reload": 72900,   "monthly": 137640,  "total_bonus": 185280,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.02948,
     "lossback_pct": 0.0, "cashback_pct": 0.10,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.3227},
    {"level": 16, "wager_threshold": 80_000_000,   "ggr": 2_400_000,  "deposit": 40_000,
     "level_up": 0,       "reload": 97200,   "monthly": 183520,  "total_bonus": 247040,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.02948,
     "lossback_pct": 0.0, "cashback_pct": 0.12,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.3427},
    {"level": 17, "wager_threshold": 100_000_000,  "ggr": 3_000_000,  "deposit": 40_000,
     "level_up": 0,       "reload": 121_500, "monthly": 229_400, "total_bonus": 308_800,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.02948,
     "lossback_pct": 0.0, "cashback_pct": 0.12,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.4027},
    {"level": 18, "wager_threshold": 200_000_000,  "ggr": 6_000_000,  "deposit": 80_000,
     "level_up": 0,       "reload": 243_000, "monthly": 458_800, "total_bonus": 617_600,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.02807,
     "lossback_pct": 0.0, "cashback_pct": 0.15,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.4327},
    {"level": 19, "wager_threshold": 350_000_000,  "ggr": 10_500_000, "deposit": 150_000,
     "level_up": 0,       "reload": 425_250, "monthly": 802_900, "total_bonus": 1_080_800,
     "bonus_pct_ggr": 0.01429, "reload_pct_ggr": 0.03033,
     "lossback_pct": 0.0, "cashback_pct": 0.15,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.4337},
    {"level": 20, "wager_threshold": 500_000_000,  "ggr": 15_000_000, "deposit": 200_000,
     "level_up": 0,       "reload": 607_500, "monthly": 1_147_000, "total_bonus": 1_544_000,
     "bonus_pct_ggr": 0.01333, "reload_pct_ggr": 0.03456,
     "lossback_pct": 0.0, "cashback_pct": 0.15,
     "casino_ops_pct": 0.0765, "sportsbook_ops_pct": 0.1029,
     "effective_cost_pct": 0.4327},
]

# ─── Fixed OPEX (Monthly, from Bluff P&L) ───────────────────────────────────

MONTHLY_OPEX = {
    "mainstream_marketing": 210_000,
    "affiliate_retainer": 192_000,
    "fireblocks": 6_954,
    "mesh_connect": 5_000,
    "cloudflare_ddos": 10_000,        # Scales: 10K→20K→30K→50K
    "hosting_aws": 10_000,            # Scales: 10K→20K→30K→50K
    "platform_elantil": 95_833.33,
    "tools_smartico_etc": 35_831,
    "amplitude": 311,
    "cs_provider_intercom": 1_000,
    "fraud_aml_sumsub": 5_632,
    "greco": 2_554.50,
    "others": 50_000,
    "headcount": 420_000,
}

# ─── Effective Bonus Scenarios (player distribution across 20 levels) ────────

BONUS_SCENARIOS = {
    1: "Conservative — heavier at lower levels",
    2: "Moderate — balanced distribution",
    3: "Aggressive — heavier at higher levels",
}

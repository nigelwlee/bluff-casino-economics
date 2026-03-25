"use client";

import { VIPPLResult } from "./types";

const API_BASE = "/api";

export interface VIPCalcParams {
  nominal_volume: number;
  assumptions: {
    level_up_pct: number;
    reload_pct: number;
    weekly_pct: number;
    monthly_pct: number;
    lossback_standard_pct: number;
    lossback_discretionary_pct: number;
    casino_ops_pct: number;
    sportsbook_ops_pct: number;
    affiliate_pct: number;
  };
}

export interface VIPCompanyImpactParams {
  vip_monthly_wagers: number;
  vip_pct_of_total: number;
  vip_bonus_pct: number;
  num_months?: number;
  growth_rate?: number;
}

export interface CompanyImpactResult {
  vip_pl: VIPPLResult;
  company_pl_with_vip: {
    months: Array<{
      month: number;
      total_wagers: number;
      ggr: { total: number };
      ngr: number;
      profit_before_opex: number;
      profit_after_opex: number;
    }>;
    cumulative: {
      wagers: number;
      ggr: number;
      ngr: number;
      profit_after_opex: number;
    };
    breakeven_month: number | null;
  };
  blended_bonus_pct: number;
}

export async function calcVIPPL(params: VIPCalcParams): Promise<VIPPLResult> {
  const response = await fetch(`${API_BASE}/calc/vip`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error(`Calc error: ${response.status}`);
  return response.json();
}

export async function calcVIPCompanyImpact(
  params: VIPCompanyImpactParams
): Promise<CompanyImpactResult> {
  const response = await fetch(`${API_BASE}/calc/company-pl/vip-impact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error(`Calc error: ${response.status}`);
  return response.json();
}

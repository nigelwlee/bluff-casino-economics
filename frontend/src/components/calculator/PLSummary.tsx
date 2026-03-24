"use client";

import { useState, useEffect, useRef } from "react";
import { CalculatorState } from "./VIPConfigurator";

const API_BASE = "/api";

const SPORTSBOOK_SHARE = 0.05;

// ─── Types ─────────────────────────────────────────────────────────────────

interface VIPResult {
  nominal_volume: number;
  weighted_volume: number;
  ggr: number;
  casino_ggr: number;
  sportsbook_ggr: number;
  ops_costs: { casino_ops: number; sportsbook_ops: number; total: number };
  bonuses: {
    level_up: number;
    reload: number;
    weekly: number;
    monthly: number;
    lossback_standard: number;
    lossback_discretionary: number;
    total: number;
  };
  ngr_before_promos: number;
  affiliate_cost: number;
  ngr_after_affiliate: number;
  promos: { total: number };
  ngr_after_promos: number;
  margins: {
    ggr_pct_of_nominal: number;
    ngr_pct_of_ggr: number;
    total_cost_pct_of_ggr: number;
  };
}

interface CompanyMonth {
  month: number;
  total_wagers: number;
  casino_wagers: number;
  sportsbook_wagers: number;
  ggr: {
    pragmatic: number;
    evo: number;
    ogs: number;
    sportsbook: number;
    casino_total: number;
    total: number;
  };
  effective_ggr_pct: number;
  bonuses: number;
  bonus_pct: number;
  ops_costs: {
    pragmatic: { cost: number; effective_rate: number };
    evo: { cost: number; effective_rate: number };
    sportsbook: { cost: number; effective_rate: number };
    casino_total: number;
    sportsbook_total: number;
    total: number;
  };
  ngr: number;
  ngr_pct_ggr: number;
  channel_costs: {
    affiliate: number;
    referral: number;
    total: number;
  };
  profit_before_opex: number;
  profit_before_opex_pct_ggr: number;
  opex: number;
  profit_after_opex: number;
  profit_after_opex_pct_ggr: number;
}

interface CompanyImpactResult {
  vip_monthly_wagers: number;
  total_monthly_wagers: number;
  vip_pct_of_total: number;
  vip_bonus_pct: number;
  non_vip_bonus_pct: number;
  blended_bonus_pct: number;
  vip_ggr_rate: number | null;
  non_vip_ggr_rate: number;
  blended_ggr_rate: number;
  projection: {
    months: CompanyMonth[];
    cumulative: {
      wagers: number;
      ggr: number;
      ngr: number;
      profit_after_opex: number;
    };
    breakeven_month: number | null;
  };
}

interface BreakevenResult {
  breakeven_total_wagers: number;
  breakeven_vip_wagers: number;
  vip_pct_of_total: number;
  blended_bonus_pct: number;
  profit_after_opex_at_breakeven: number;
  ggr_at_breakeven: number;
  ngr_at_breakeven: number;
  opex: number;
}

// ─── Helpers ───────────────────────────────────────────────────────────────

function fmt(v: number): string {
  const abs = Math.abs(v);
  const sign = v < 0 ? "-" : "";
  return `${sign}$${abs.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function PLRow({
  label,
  value,
  pctValue,
  bold,
  indent,
  highlight,
}: {
  label: string;
  value: number;
  pctValue?: string;
  bold?: boolean;
  indent?: boolean;
  highlight?: "green" | "red" | "yellow";
}) {
  const colorClass = highlight === "green"
    ? "text-green-400"
    : highlight === "red"
    ? "text-red-400"
    : highlight === "yellow"
    ? "text-yellow-400"
    : "text-gray-300";
  return (
    <div className={`flex justify-between py-1 ${indent ? "pl-4" : ""} ${bold ? "font-semibold" : ""}`}>
      <span className={`text-xs ${indent ? "text-gray-500" : "text-gray-300"}`}>{label}</span>
      <div className="flex items-center gap-2">
        {pctValue && <span className="text-xs text-gray-600 font-mono">{pctValue}</span>}
        <span className={`text-xs font-mono ${colorClass} w-28 text-right`}>{fmt(value)}</span>
      </div>
    </div>
  );
}

function InfoRow({
  label,
  value,
  muted,
}: {
  label: string;
  value: string;
  muted?: boolean;
}) {
  return (
    <div className="flex justify-between py-0.5">
      <span className={`text-xs ${muted ? "text-gray-600" : "text-gray-500"}`}>{label}</span>
      <span className={`text-xs font-mono ${muted ? "text-gray-600" : "text-gray-400"}`}>{value}</span>
    </div>
  );
}

function SectionHeader({ label, accent }: { label: string; accent: "blue" | "emerald" }) {
  const borderColor = accent === "blue" ? "border-blue-500" : "border-emerald-500";
  const textColor = accent === "blue" ? "text-blue-400" : "text-emerald-400";
  return (
    <div className={`flex items-center gap-2 mb-4 border-l-2 ${borderColor} pl-3`}>
      <h2 className={`text-sm font-bold ${textColor} uppercase tracking-wide`}>{label}</h2>
    </div>
  );
}

// ─── Component ─────────────────────────────────────────────────────────────

export function PLSummary({
  state,
  onApplyBreakeven,
}: {
  state: CalculatorState | null;
  onApplyBreakeven?: (vipWagers: number, companyWagers: number) => void;
}) {
  const [vipResult, setVipResult] = useState<VIPResult | null>(null);
  const [companyResult, setCompanyResult] = useState<CompanyImpactResult | null>(null);
  const [breakevenResult, setBreakevenResult] = useState<BreakevenResult | null>(null);
  const [breakevenLoading, setBreakevenLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    if (!state || state.monthlyVolume <= 0) {
      setVipResult(null);
      setCompanyResult(null);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const casinoShare = 1 - SPORTSBOOK_SHARE;
        const sportsbookRtp = 0.93;
        const casinoRtp = (state.effectiveRtp - SPORTSBOOK_SHARE * sportsbookRtp) / casinoShare;
        const casinoEdge = Math.max(0, 1 - casinoRtp);
        const sportsbookEdge = 1 - sportsbookRtp;

        const wagerMix = [
          { category: "casino", share: casinoShare, rtp: casinoRtp, edge: casinoEdge, adj_factor: 1.0 },
          { category: "sportsbook", share: SPORTSBOOK_SHARE, rtp: sportsbookRtp, edge: sportsbookEdge, adj_factor: 1.0 },
        ];

        const vipRes = await fetch(`${API_BASE}/calc/vip`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nominal_volume: state.monthlyVolume,
            wager_mix: wagerMix,
            assumptions: state.bonuses,
          }),
        });
        if (!vipRes.ok) throw new Error(`VIP calc error: ${vipRes.status}`);
        const vipData: VIPResult = await vipRes.json();
        setVipResult(vipData);

        const vipBonusPct = vipData.ggr !== 0
          ? Math.abs(vipData.bonuses.total) / vipData.ggr
          : 0;

        const companyVipPct = state.company.companyMonthlyWagers > 0
          ? state.monthlyVolume / state.company.companyMonthlyWagers
          : 0;

        const companyRes = await fetch(`${API_BASE}/calc/company-pl/vip-impact`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            vip_monthly_wagers: state.monthlyVolume,
            vip_pct_of_total: companyVipPct,
            vip_bonus_pct: vipBonusPct,
            non_vip_bonus_pct: state.company.nonVipBonusPct,
            vip_ggr_rate: 1 - state.effectiveRtp,
            num_months: 1,
            overrides: {
              opex_overrides: { total_opex: state.company.monthlyOpex },
            },
          }),
        });
        if (!companyRes.ok) throw new Error(`Company calc error: ${companyRes.status}`);
        const companyData: CompanyImpactResult = await companyRes.json();
        setCompanyResult(companyData);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Calculation failed");
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [state]);

  if (!state) {
    return (
      <div className="flex items-center justify-center h-full text-gray-600 text-sm">
        Configure inputs to see P&L
      </div>
    );
  }

  if (loading && !vipResult) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500 text-sm">
        Calculating...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-800 rounded-lg p-3 text-red-400 text-xs">
        {error}
      </div>
    );
  }

  if (!vipResult) return null;

  const totalBonusPct = vipResult.ggr !== 0
    ? Math.abs(vipResult.bonuses.total) / vipResult.ggr
    : 0;
  const ggrRate = 1 - state.effectiveRtp;
  const companyMonth1 = companyResult?.projection.months[0];
  const companyVipPct = state.company.companyMonthlyWagers > 0
    ? state.monthlyVolume / state.company.companyMonthlyWagers
    : 0;

  return (
    <div className="space-y-6">
      {loading && <div className="text-xs text-gray-500">Recalculating...</div>}

      {/* ═══════════════════════════════════════════════════════════════════
          VIP SECTION
          ═══════════════════════════════════════════════════════════════════ */}
      <div>
        <SectionHeader label="VIP Player Economics" accent="blue" />

        {/* VIP KPI Cards */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">VIP Wagers</div>
            <div className="text-lg font-bold text-white font-mono">{fmt(state.monthlyVolume)}</div>
            <div className="text-xs text-gray-500 mt-0.5">per month</div>
          </div>
          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">GGR</div>
            <div className="text-lg font-bold text-white font-mono">{fmt(vipResult.ggr)}</div>
            <div className="text-xs text-gray-500 mt-0.5">{pct(ggrRate)} of wagers</div>
          </div>
          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Net Revenue</div>
            <div className={`text-lg font-bold font-mono ${vipResult.ngr_after_promos >= 0 ? "text-green-400" : "text-red-400"}`}>
              {fmt(vipResult.ngr_after_promos)}
            </div>
            <div className="text-xs text-gray-500 mt-0.5">{pct(vipResult.margins.ngr_pct_of_ggr)} of GGR</div>
          </div>
          <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Total Cost</div>
            <div className="text-lg font-bold text-red-400 font-mono">{pct(vipResult.margins.total_cost_pct_of_ggr)}</div>
            <div className="text-xs text-gray-500 mt-0.5">of GGR</div>
          </div>
        </div>

        {/* VIP P&L Breakdown */}
        <div className="bg-blue-950/20 border border-blue-900/40 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-3">P&L Waterfall</h3>
          <div className="divide-y divide-gray-700/50">
            <PLRow label="Gross Gaming Revenue (GGR)" value={vipResult.ggr} bold highlight="green" pctValue={pct(ggrRate)} />
            <div className="py-1">
              <PLRow label="Casino Ops" value={vipResult.ops_costs.casino_ops} indent pctValue={pct(state.bonuses.casino_ops_pct)} />
              <PLRow label="Sportsbook Ops" value={vipResult.ops_costs.sportsbook_ops} indent pctValue={pct(state.bonuses.sportsbook_ops_pct)} />
            </div>
            <div className="py-1">
              <PLRow label="Level Up Bonus" value={vipResult.bonuses.level_up} indent pctValue={pct(state.bonuses.level_up_pct)} />
              <PLRow label="Reload Bonus" value={vipResult.bonuses.reload} indent pctValue={pct(state.bonuses.reload_pct)} />
              <PLRow label="Weekly Bonus" value={vipResult.bonuses.weekly} indent pctValue={pct(state.bonuses.weekly_pct)} />
              <PLRow label="Monthly Bonus" value={vipResult.bonuses.monthly} indent pctValue={pct(state.bonuses.monthly_pct)} />
              <PLRow label="Lossback (Standard)" value={vipResult.bonuses.lossback_standard} indent pctValue={pct(state.bonuses.lossback_standard_pct)} />
              <PLRow label="Lossback (Discretionary)" value={vipResult.bonuses.lossback_discretionary} indent pctValue={pct(state.bonuses.lossback_discretionary_pct)} />
              <PLRow label="Total Bonuses" value={vipResult.bonuses.total} bold highlight="red" pctValue={pct(totalBonusPct)} />
            </div>
            <PLRow label="NGR (before promos)" value={vipResult.ngr_before_promos} bold />
            <PLRow label="Affiliate Cost" value={vipResult.affiliate_cost} indent highlight="red" pctValue={pct(state.bonuses.affiliate_pct)} />
            <PLRow label="NGR (after affiliate)" value={vipResult.ngr_after_affiliate} bold />
            {vipResult.promos.total !== 0 && (
              <PLRow label="Additional Promos" value={vipResult.promos.total} indent highlight="red" />
            )}
            <PLRow
              label="Final NGR"
              value={vipResult.ngr_after_promos}
              bold
              highlight={vipResult.ngr_after_promos >= 0 ? "green" : "red"}
            />
          </div>
        </div>

        {/* VIP Cost Breakdown Bars */}
        <div className="bg-blue-950/20 border border-blue-900/40 rounded-lg p-4 mt-3">
          <h3 className="text-sm font-semibold text-white mb-3">Cost Breakdown (% of GGR)</h3>
          <div className="space-y-1.5">
            {[
              { label: "Ops Costs", value: vipResult.ggr ? Math.abs(vipResult.ops_costs.total) / vipResult.ggr : 0, color: "bg-blue-500" },
              { label: "Bonuses", value: totalBonusPct, color: "bg-red-500" },
              { label: "Affiliate", value: vipResult.ggr ? Math.abs(vipResult.affiliate_cost) / vipResult.ggr : 0, color: "bg-purple-500" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs mb-0.5">
                  <span className="text-gray-400">{item.label}</span>
                  <span className="text-gray-300 font-mono">{(item.value * 100).toFixed(1)}%</span>
                </div>
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} rounded-full transition-all duration-300`}
                    style={{ width: `${Math.min(item.value * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
            <div className="border-t border-gray-700 pt-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-gray-300 font-semibold">Retained</span>
                <span className={`font-mono font-semibold ${vipResult.margins.ngr_pct_of_ggr >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {(vipResult.margins.ngr_pct_of_ggr * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          COMPANY SECTION
          ═══════════════════════════════════════════════════════════════════ */}
      {companyResult && companyMonth1 && (
        <div>
          <SectionHeader label="Company P&L" accent="emerald" />

          {/* Company Assumptions (read-only) */}
          <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-lg p-4 mb-3">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Assumptions</h3>
            <div className="grid grid-cols-2 gap-x-6 gap-y-0.5">
              <InfoRow label="Casino / Sportsbook split" value="92% / 8%" />
              <InfoRow label="Provider / OG split" value="50% / 50%" />
              <InfoRow label="Provider RTP" value="97.00%" />
              <InfoRow label="OG RTP" value="99.00%" />
              <InfoRow label="Sportsbook RTP" value="92.00%" />
              <InfoRow label="Effective GGR rate" value={pct(companyMonth1.effective_ggr_pct)} />
              <InfoRow label="Pragmatic / Evo split" value="40% / 60%" />
              <InfoRow label="Affiliate channel" value="50% vol, 30% NGR" />
              <InfoRow label="Referral channel" value="5% vol, 22% NGR" />
              <InfoRow label="VIP % of total volume" value={pct(companyVipPct)} />
              <InfoRow label="VIP bonus rate" value={pct(companyResult.vip_bonus_pct)} />
              <InfoRow label="Non-VIP bonus rate" value={pct(companyResult.non_vip_bonus_pct)} />
              <InfoRow label="Blended bonus rate" value={pct(companyResult.blended_bonus_pct)} />
              <InfoRow label="Monthly OPEX" value={fmt(Math.abs(companyMonth1.opex))} />
            </div>
          </div>

          {/* Company P&L Breakdown */}
          <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-white mb-3">Monthly P&L</h3>
            <div className="divide-y divide-gray-700/50">
              {/* Wagers */}
              <PLRow label="Total Wagers" value={companyMonth1.total_wagers} bold />
              <div className="py-1">
                <PLRow label="Casino Wagers" value={companyMonth1.casino_wagers} indent pctValue="92%" />
                <PLRow label="Sportsbook Wagers" value={companyMonth1.sportsbook_wagers} indent pctValue="8%" />
              </div>

              {/* GGR */}
              <PLRow label="Gross Gaming Revenue (GGR)" value={companyMonth1.ggr.total} bold highlight="green" pctValue={pct(companyMonth1.effective_ggr_pct)} />
              <div className="py-1">
                <PLRow label="Pragmatic" value={companyMonth1.ggr.pragmatic} indent />
                <PLRow label="Evo" value={companyMonth1.ggr.evo} indent />
                <PLRow label="OGs" value={companyMonth1.ggr.ogs} indent />
                <PLRow label="Sportsbook" value={companyMonth1.ggr.sportsbook} indent />
              </div>

              {/* Bonuses */}
              <PLRow label="Bonuses" value={companyMonth1.bonuses} bold highlight="red" pctValue={pct(companyMonth1.bonus_pct)} />

              {/* Ops Costs */}
              <div className="py-1">
                <PLRow label="Pragmatic Ops" value={companyMonth1.ops_costs.pragmatic.cost} indent pctValue={pct(companyMonth1.ops_costs.pragmatic.effective_rate)} />
                <PLRow label="Evo Ops" value={companyMonth1.ops_costs.evo.cost} indent pctValue={pct(companyMonth1.ops_costs.evo.effective_rate)} />
                <PLRow label="Sportsbook Ops" value={companyMonth1.ops_costs.sportsbook.cost} indent pctValue={pct(companyMonth1.ops_costs.sportsbook.effective_rate)} />
                <PLRow label="Total Ops Costs" value={companyMonth1.ops_costs.total} bold highlight="red" />
              </div>

              {/* NGR */}
              <PLRow label="NGR" value={companyMonth1.ngr} bold highlight={companyMonth1.ngr >= 0 ? "green" : "red"} pctValue={pct(companyMonth1.ngr_pct_ggr)} />

              {/* Channel Costs */}
              <div className="py-1">
                <PLRow label="Affiliate Cost" value={companyMonth1.channel_costs.affiliate} indent />
                <PLRow label="Referral Cost" value={companyMonth1.channel_costs.referral} indent />
                <PLRow label="Total Channel Costs" value={companyMonth1.channel_costs.total} bold highlight="red" />
              </div>

              {/* Profit */}
              <PLRow label="Profit before OPEX" value={companyMonth1.profit_before_opex} bold pctValue={pct(companyMonth1.profit_before_opex_pct_ggr)} />
              <PLRow label="OPEX" value={companyMonth1.opex} highlight="red" />
              <PLRow
                label="Profit after OPEX"
                value={companyMonth1.profit_after_opex}
                bold
                highlight={companyMonth1.profit_after_opex >= 0 ? "green" : "red"}
                pctValue={pct(companyMonth1.profit_after_opex_pct_ggr)}
              />
            </div>
          </div>

          {/* Breakeven Goal Seek */}
          <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-lg p-4 mt-3">
            <button
              onClick={async () => {
                if (!state || !vipResult) return;
                setBreakevenLoading(true);
                try {
                  const vipBonusPct = vipResult.ggr !== 0
                    ? Math.abs(vipResult.bonuses.total) / vipResult.ggr
                    : 0;
                  const res = await fetch(`${API_BASE}/calc/company-pl/breakeven`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      vip_pct_of_total: companyVipPct,
                      vip_bonus_pct: vipBonusPct,
                      non_vip_bonus_pct: state.company.nonVipBonusPct,
                      vip_ggr_rate: 1 - state.effectiveRtp,
                      overrides: {
                        opex_overrides: { total_opex: state.company.monthlyOpex },
                      },
                    }),
                  });
                  if (!res.ok) throw new Error(`Breakeven error: ${res.status}`);
                  const data: BreakevenResult = await res.json();
                  setBreakevenResult(data);
                } catch {
                  setBreakevenResult(null);
                } finally {
                  setBreakevenLoading(false);
                }
              }}
              disabled={breakevenLoading}
              className="w-full text-xs px-3 py-2 rounded-lg border border-yellow-700 text-yellow-400 hover:bg-yellow-900/20 hover:border-yellow-600 disabled:opacity-50 transition-colors"
            >
              {breakevenLoading ? "Calculating..." : "Find Breakeven Volume"}
            </button>

            {breakevenResult && (
              <div className="mt-3 space-y-1.5">
                <div className="text-xs text-gray-500 font-semibold">
                  Breakeven at {pct(breakevenResult.vip_pct_of_total)} VIP mix:
                </div>
                <div className="divide-y divide-gray-700/50">
                  <PLRow label="Total Company Wagers" value={breakevenResult.breakeven_total_wagers} />
                  <PLRow label="VIP Wagers" value={breakevenResult.breakeven_vip_wagers} />
                  <PLRow label="GGR at Breakeven" value={breakevenResult.ggr_at_breakeven} />
                  <PLRow label="Profit after OPEX" value={breakevenResult.profit_after_opex_at_breakeven} highlight={breakevenResult.profit_after_opex_at_breakeven >= 0 ? "green" : "red"} />
                </div>
                {onApplyBreakeven && (
                  <button
                    onClick={() => onApplyBreakeven(
                      breakevenResult.breakeven_vip_wagers,
                      breakevenResult.breakeven_total_wagers
                    )}
                    className="w-full mt-2 text-xs px-3 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
                  >
                    Apply Breakeven Volumes
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

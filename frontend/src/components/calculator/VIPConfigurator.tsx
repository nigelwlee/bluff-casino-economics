"use client";

import { useState, useEffect, useCallback } from "react";

interface BonusAssumptions {
  level_up_pct: number;
  reload_pct: number;
  weekly_pct: number;
  monthly_pct: number;
  lossback_standard_pct: number;
  lossback_discretionary_pct: number;
  casino_ops_pct: number;
  sportsbook_ops_pct: number;
  affiliate_pct: number;
}

export interface CompanyAssumptions {
  companyMonthlyWagers: number;
  nonVipBonusPct: number;
  monthlyOpex: number;
}

export interface CalculatorState {
  monthlyVolume: number;
  effectiveRtp: number;
  bonuses: BonusAssumptions;
  company: CompanyAssumptions;
}

const DEFAULT_BONUSES: BonusAssumptions = {
  level_up_pct: 0.05,
  reload_pct: 0.10,
  weekly_pct: 0.03,
  monthly_pct: 0.07,
  lossback_standard_pct: 0.30,
  lossback_discretionary_pct: 0.00,
  casino_ops_pct: 0.10,
  sportsbook_ops_pct: 0.11,
  affiliate_pct: 0.25,
};

const DEFAULT_MONTHLY_OPEX = 1_045_116;

function formatNumberWithCommas(value: number): string {
  return value.toLocaleString("en-US");
}

function parseFormattedNumber(value: string): number {
  return parseFloat(value.replace(/,/g, "")) || 0;
}

function MoneyInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  const [displayValue, setDisplayValue] = useState(formatNumberWithCommas(value));
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    if (!focused) {
      setDisplayValue(formatNumberWithCommas(value));
    }
  }, [value, focused]);

  return (
    <div>
      <label className="text-xs text-gray-400 block mb-1.5">{label}</label>
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-400">$</span>
        <input
          type="text"
          inputMode="numeric"
          value={displayValue}
          onFocus={() => {
            setFocused(true);
            setDisplayValue(value.toString());
          }}
          onBlur={() => {
            setFocused(false);
            const parsed = parseFormattedNumber(displayValue);
            onChange(parsed);
            setDisplayValue(formatNumberWithCommas(parsed));
          }}
          onChange={(e) => {
            setDisplayValue(e.target.value);
            const parsed = parseFormattedNumber(e.target.value);
            if (!isNaN(parsed)) onChange(parsed);
          }}
          className="bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-white font-mono w-full focus:border-blue-500 focus:outline-none"
        />
      </div>
    </div>
  );
}

function PctInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <label className="text-xs text-gray-400">{label}</label>
      <div className="flex items-center gap-1">
        <input
          type="number"
          value={parseFloat((value * 100).toFixed(2))}
          onChange={(e) => {
            const pct = parseFloat(e.target.value);
            if (!isNaN(pct)) onChange(pct / 100);
          }}
          step={0.5}
          min={0}
          className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-white font-mono w-20 text-right focus:border-blue-500 focus:outline-none"
        />
        <span className="text-xs text-gray-500">%</span>
      </div>
    </div>
  );
}

export function VIPConfigurator({
  onChange,
  externalVolumes,
  onExternalApplied,
}: {
  onChange: (state: CalculatorState) => void;
  externalVolumes?: { vipWagers: number; companyWagers: number } | null;
  onExternalApplied?: () => void;
}) {
  const [monthlyVolume, setMonthlyVolume] = useState(80_000_000);
  const [effectiveRtp, setEffectiveRtp] = useState(0.9838);
  const [bonuses, setBonuses] = useState<BonusAssumptions>(DEFAULT_BONUSES);
  const [company, setCompany] = useState<CompanyAssumptions>({
    companyMonthlyWagers: 100_000_000,
    nonVipBonusPct: 0.292,
    monthlyOpex: 1_000_000,
  });

  // Apply external volume updates (e.g. from breakeven goal seek)
  useEffect(() => {
    if (externalVolumes) {
      setMonthlyVolume(Math.round(externalVolumes.vipWagers));
      setCompany((c) => ({ ...c, companyMonthlyWagers: Math.round(externalVolumes.companyWagers) }));
      onExternalApplied?.();
    }
  }, [externalVolumes, onExternalApplied]);

  const emitChange = useCallback(() => {
    onChange({ monthlyVolume, effectiveRtp, bonuses, company });
  }, [monthlyVolume, effectiveRtp, bonuses, company, onChange]);

  useEffect(() => {
    emitChange();
  }, [emitChange]);

  const updateBonus = (key: keyof BonusAssumptions, value: number) => {
    setBonuses((b) => ({ ...b, [key]: value }));
  };

  const updateCompany = (key: keyof CompanyAssumptions, value: number) => {
    setCompany((c) => ({ ...c, [key]: value }));
  };

  // Derived values
  const vipBonusPct = bonuses.level_up_pct + bonuses.reload_pct + bonuses.weekly_pct
    + bonuses.monthly_pct + bonuses.lossback_standard_pct + bonuses.lossback_discretionary_pct;
  const vipGgrRate = 1 - effectiveRtp;
  const companyGgrRate = 0.0248;
  const vipPctOfTotal = company.companyMonthlyWagers > 0
    ? monthlyVolume / company.companyMonthlyWagers
    : 0;
  const nonVipPct = 1 - vipPctOfTotal;
  const blendedBonusPct = (vipPctOfTotal * vipBonusPct) + (nonVipPct * company.nonVipBonusPct);

  return (
    <div className="space-y-5">
      {/* VIP Inputs */}
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">VIP Assumptions</h3>
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 space-y-3">
          <MoneyInput
            label="Total Monthly Wager Volume from VIPs"
            value={monthlyVolume}
            onChange={setMonthlyVolume}
          />
          <PctInput
            label="Effective RTP"
            value={effectiveRtp}
            onChange={(v) => setEffectiveRtp(v)}
          />
          <div className="text-xs text-gray-500">
            GGR rate: <span className="text-white font-mono">{(vipGgrRate * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>

      {/* Bonus & Promo Rates */}
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Bonus & Promo Rates</h3>
        <div className="space-y-2 bg-gray-800/50 border border-gray-700 rounded-lg p-3">
          <PctInput label="Level Up" value={bonuses.level_up_pct} onChange={(v) => updateBonus("level_up_pct", v)} />
          <PctInput label="Reload" value={bonuses.reload_pct} onChange={(v) => updateBonus("reload_pct", v)} />
          <PctInput label="Weekly" value={bonuses.weekly_pct} onChange={(v) => updateBonus("weekly_pct", v)} />
          <PctInput label="Monthly" value={bonuses.monthly_pct} onChange={(v) => updateBonus("monthly_pct", v)} />
          <div className="border-t border-gray-700 pt-2">
            <PctInput label="Lossback (Standard)" value={bonuses.lossback_standard_pct} onChange={(v) => updateBonus("lossback_standard_pct", v)} />
          </div>
          <PctInput label="Lossback (Discretionary)" value={bonuses.lossback_discretionary_pct} onChange={(v) => updateBonus("lossback_discretionary_pct", v)} />
        </div>
      </div>

      {/* Ops & Affiliate Costs */}
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Ops & Affiliate Costs</h3>
        <div className="space-y-2 bg-gray-800/50 border border-gray-700 rounded-lg p-3">
          <PctInput label="Casino Ops" value={bonuses.casino_ops_pct} onChange={(v) => updateBonus("casino_ops_pct", v)} />
          <PctInput label="Sportsbook Ops" value={bonuses.sportsbook_ops_pct} onChange={(v) => updateBonus("sportsbook_ops_pct", v)} />
          <PctInput label="Affiliate Cost" value={bonuses.affiliate_pct} onChange={(v) => updateBonus("affiliate_pct", v)} />
        </div>
      </div>

      {/* Company Assumptions */}
      <div>
        <div className="flex items-center gap-2 mb-3 border-l-2 border-emerald-500 pl-3">
          <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wide">Company Assumptions</h3>
        </div>
        <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-lg p-3 space-y-3">
          <MoneyInput
            label="Total Company Wagers / Month"
            value={company.companyMonthlyWagers}
            onChange={(v) => updateCompany("companyMonthlyWagers", v)}
          />

          <div className="border-t border-gray-700 pt-3 mt-3">
            <div className="flex justify-between text-xs mb-2">
              <span className="text-gray-500 font-semibold">VIP Segment</span>
              <span className="text-white font-mono">{(vipPctOfTotal * 100).toFixed(1)}% of volume</span>
            </div>
            <div className="space-y-1 ml-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Effective RTP</span>
                <span className="text-white font-mono">{(effectiveRtp * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">GGR Rate</span>
                <span className="text-white font-mono">{(vipGgrRate * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Bonus Rate (% of GGR)</span>
                <span className="text-white font-mono">{(vipBonusPct * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-700 pt-3">
            <div className="flex justify-between text-xs mb-2">
              <span className="text-gray-500 font-semibold">Non-VIP Segment</span>
              <span className="text-white font-mono">{(nonVipPct * 100).toFixed(1)}% of volume</span>
            </div>
            <div className="space-y-1 ml-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Effective GGR Rate</span>
                <span className="text-white font-mono">{(companyGgrRate * 100).toFixed(2)}%</span>
              </div>
              <PctInput label="Bonus Rate (% of GGR)" value={company.nonVipBonusPct} onChange={(v) => updateCompany("nonVipBonusPct", v)} />
            </div>
          </div>

          <div className="border-t border-gray-700 pt-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400 font-semibold">Blended Bonus Rate</span>
              <span className="text-white font-mono font-semibold">{(blendedBonusPct * 100).toFixed(1)}%</span>
            </div>
            <div className="text-xs text-gray-600">
              ({(vipPctOfTotal * 100).toFixed(0)}% x {(vipBonusPct * 100).toFixed(0)}%) + ({(nonVipPct * 100).toFixed(0)}% x {(company.nonVipBonusPct * 100).toFixed(0)}%)
            </div>
          </div>

          <div className="border-t border-gray-700 pt-3">
            <MoneyInput
              label="Monthly OPEX"
              value={company.monthlyOpex}
              onChange={(v) => updateCompany("monthlyOpex", v)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

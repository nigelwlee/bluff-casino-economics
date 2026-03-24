"use client";

interface PLRow {
  label: string;
  value: number;
  indent?: boolean;
  bold?: boolean;
  highlight?: boolean;
  pctOfGgr?: number;
}

function formatCurrency(value: number): string {
  const abs = Math.abs(value);
  const formatted =
    abs >= 1_000_000
      ? `$${(abs / 1_000_000).toFixed(2)}M`
      : abs >= 1_000
      ? `$${(abs / 1_000).toFixed(1)}K`
      : `$${abs.toFixed(2)}`;
  return value < 0 ? `-${formatted}` : formatted;
}

function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function PLTable({
  title,
  rows,
}: {
  title: string;
  rows: PLRow[];
}) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      <div className="divide-y divide-gray-800">
        {rows.map((row, i) => (
          <div
            key={i}
            className={`flex items-center justify-between px-4 py-2 text-sm ${
              row.highlight
                ? "bg-blue-950/30 border-l-2 border-blue-500"
                : ""
            }`}
          >
            <span
              className={`${row.indent ? "pl-4" : ""} ${
                row.bold ? "font-semibold text-white" : "text-gray-400"
              }`}
            >
              {row.label}
            </span>
            <div className="flex items-center gap-4">
              <span
                className={`font-mono ${
                  row.value < 0 ? "text-red-400" : "text-green-400"
                } ${row.bold ? "font-semibold" : ""}`}
              >
                {formatCurrency(row.value)}
              </span>
              {row.pctOfGgr !== undefined && (
                <span className="text-xs text-gray-500 w-16 text-right">
                  {formatPct(row.pctOfGgr)}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function VIPPLTable({ result }: { result: Record<string, unknown> }) {
  const r = result as {
    tier: string;
    ggr: number;
    ops_costs: { casino_ops: number; sportsbook_ops: number; total: number };
    bonuses: {
      level_up: number;
      reload: number;
      weekly: number;
      monthly: number;
      lossback_standard: number;
      total: number;
    };
    ngr_before_promos: number;
    affiliate_cost: number;
    ngr_after_affiliate: number;
    ngr_after_promos: number;
  };

  const ggr = r.ggr;

  const rows: PLRow[] = [
    { label: "GGR", value: r.ggr, bold: true, pctOfGgr: 1.0 },
    {
      label: "Casino Ops",
      value: r.ops_costs.casino_ops,
      indent: true,
      pctOfGgr: r.ops_costs.casino_ops / ggr,
    },
    {
      label: "Sportsbook Ops",
      value: r.ops_costs.sportsbook_ops,
      indent: true,
      pctOfGgr: r.ops_costs.sportsbook_ops / ggr,
    },
    {
      label: "Level Up",
      value: r.bonuses.level_up,
      indent: true,
      pctOfGgr: r.bonuses.level_up / ggr,
    },
    {
      label: "Reload",
      value: r.bonuses.reload,
      indent: true,
      pctOfGgr: r.bonuses.reload / ggr,
    },
    {
      label: "Weekly",
      value: r.bonuses.weekly,
      indent: true,
      pctOfGgr: r.bonuses.weekly / ggr,
    },
    {
      label: "Monthly",
      value: r.bonuses.monthly,
      indent: true,
      pctOfGgr: r.bonuses.monthly / ggr,
    },
    {
      label: "Lossback",
      value: r.bonuses.lossback_standard,
      indent: true,
      pctOfGgr: r.bonuses.lossback_standard / ggr,
    },
    {
      label: "NGR Before Promos",
      value: r.ngr_before_promos,
      bold: true,
      highlight: true,
      pctOfGgr: r.ngr_before_promos / ggr,
    },
    {
      label: "Affiliate Cost",
      value: r.affiliate_cost,
      indent: true,
      pctOfGgr: r.affiliate_cost / ggr,
    },
    {
      label: "NGR After Promos",
      value: r.ngr_after_promos,
      bold: true,
      highlight: true,
      pctOfGgr: r.ngr_after_promos / ggr,
    },
  ];

  const tierLabel = r.tier
    ? r.tier.charAt(0).toUpperCase() + r.tier.slice(1)
    : "Custom";

  return <PLTable title={`${tierLabel} P&L`} rows={rows} />;
}

"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

interface WaterfallItem {
  name: string;
  value: number;
}

export function WaterfallChart({ result }: { result: Record<string, unknown> }) {
  const r = result as {
    ggr: number;
    ops_costs: { casino_ops: number; sportsbook_ops: number };
    bonuses: { total: number };
    affiliate_cost: number;
    ngr_after_promos: number;
  };

  const items: WaterfallItem[] = [
    { name: "GGR", value: r.ggr },
    { name: "Casino Ops", value: r.ops_costs.casino_ops },
    { name: "SB Ops", value: r.ops_costs.sportsbook_ops },
    { name: "Bonuses", value: r.bonuses.total },
    { name: "Affiliate", value: r.affiliate_cost },
    { name: "NGR", value: r.ngr_after_promos },
  ];

  // Build waterfall data with running totals
  let runningTotal = 0;
  const chartData = items.map((item, i) => {
    if (i === 0) {
      // First bar: starts from 0
      runningTotal = item.value;
      return { name: item.name, base: 0, value: item.value, isTotal: false };
    }
    if (i === items.length - 1) {
      // Last bar: final NGR total
      return { name: item.name, base: 0, value: item.value, isTotal: true };
    }
    // Middle bars: floating
    const base = runningTotal + item.value; // after deduction
    const barValue = Math.abs(item.value);
    const start = Math.min(runningTotal, base);
    runningTotal = base;
    return { name: item.name, base: start, value: barValue, isTotal: false };
  });

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white">
          GGR to NGR Waterfall
        </h3>
      </div>
      <div className="p-4" style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} barCategoryGap="20%">
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="name"
              tick={{ fill: "#9CA3AF", fontSize: 12 }}
              axisLine={{ stroke: "#4B5563" }}
            />
            <YAxis
              tick={{ fill: "#9CA3AF", fontSize: 12 }}
              axisLine={{ stroke: "#4B5563" }}
              tickFormatter={(v: number) =>
                v >= 1000 ? `$${(v / 1000).toFixed(0)}K` : `$${v}`
              }
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1F2937",
                border: "1px solid #374151",
                borderRadius: 8,
                color: "#F3F4F6",
              }}
              formatter={(value) => [`$${Number(value).toLocaleString()}`, ""]}
            />
            <ReferenceLine y={0} stroke="#4B5563" />
            {/* Invisible base bar */}
            <Bar dataKey="base" stackId="a" fill="transparent" />
            {/* Visible value bar */}
            <Bar dataKey="value" stackId="a" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={
                    i === 0
                      ? "#3B82F6"
                      : i === chartData.length - 1
                      ? entry.value >= 0
                        ? "#10B981"
                        : "#EF4444"
                      : "#EF4444"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

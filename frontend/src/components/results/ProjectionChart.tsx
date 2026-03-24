"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";

export function ProjectionChart({
  result,
}: {
  result: Record<string, unknown>;
}) {
  const r = result as {
    months: Array<{
      month: number;
      total_wagers: number;
      ggr: { total: number };
      ngr: number;
      profit_after_opex: number;
    }>;
    breakeven_month: number | null;
  };

  const chartData = r.months.map((m) => ({
    month: `M${m.month}`,
    GGR: Math.round(m.ggr.total),
    NGR: Math.round(m.ngr),
    Profit: Math.round(m.profit_after_opex),
  }));

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">
          {r.months.length}-Month Projection
        </h3>
        {r.breakeven_month && (
          <span className="text-xs text-green-400 bg-green-950/40 px-2 py-1 rounded">
            Breakeven: Month {r.breakeven_month}
          </span>
        )}
      </div>
      <div className="p-4" style={{ height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="month"
              tick={{ fill: "#9CA3AF", fontSize: 11 }}
              axisLine={{ stroke: "#4B5563" }}
            />
            <YAxis
              tick={{ fill: "#9CA3AF", fontSize: 11 }}
              axisLine={{ stroke: "#4B5563" }}
              tickFormatter={(v: number) => {
                if (Math.abs(v) >= 1_000_000)
                  return `$${(v / 1_000_000).toFixed(1)}M`;
                if (Math.abs(v) >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
                return `$${v}`;
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1F2937",
                border: "1px solid #374151",
                borderRadius: 8,
                color: "#F3F4F6",
              }}
              formatter={(value) => [
                `$${Number(value).toLocaleString()}`,
                "",
              ]}
            />
            <Legend wrapperStyle={{ color: "#9CA3AF" }} />
            <ReferenceLine y={0} stroke="#6B7280" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="GGR"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="NGR"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Profit"
              stroke="#10B981"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

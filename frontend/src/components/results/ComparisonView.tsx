"use client";

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

interface ComparisonRow {
  label: string;
  valueA: number;
  valueB: number;
  bold?: boolean;
}

export function ComparisonView({
  result,
}: {
  result: Record<string, unknown>;
}) {
  const r = result as {
    delta: Record<string, number>;
    [key: string]: unknown;
  };

  // Get scenario names (the keys that aren't "delta")
  const scenarioNames = Object.keys(r).filter((k) => k !== "delta");
  if (scenarioNames.length < 2) return null;

  const scenarioA = r[scenarioNames[0]] as Record<string, unknown>;
  const scenarioB = r[scenarioNames[1]] as Record<string, unknown>;

  const rows: ComparisonRow[] = [
    {
      label: "GGR",
      valueA: (scenarioA as { ggr: number }).ggr,
      valueB: (scenarioB as { ggr: number }).ggr,
      bold: true,
    },
    {
      label: "Total Ops",
      valueA: ((scenarioA as { ops_costs: { total: number } }).ops_costs).total,
      valueB: ((scenarioB as { ops_costs: { total: number } }).ops_costs).total,
    },
    {
      label: "Total Bonuses",
      valueA: ((scenarioA as { bonuses: { total: number } }).bonuses).total,
      valueB: ((scenarioB as { bonuses: { total: number } }).bonuses).total,
    },
    {
      label: "NGR Before Promos",
      valueA: (scenarioA as { ngr_before_promos: number }).ngr_before_promos,
      valueB: (scenarioB as { ngr_before_promos: number }).ngr_before_promos,
      bold: true,
    },
    {
      label: "NGR After Promos",
      valueA: (scenarioA as { ngr_after_promos: number }).ngr_after_promos,
      valueB: (scenarioB as { ngr_after_promos: number }).ngr_after_promos,
      bold: true,
    },
  ];

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white">Scenario Comparison</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-700 text-gray-400">
            <th className="text-left px-4 py-2 font-medium">Metric</th>
            <th className="text-right px-4 py-2 font-medium">
              {scenarioNames[0]}
            </th>
            <th className="text-right px-4 py-2 font-medium">
              {scenarioNames[1]}
            </th>
            <th className="text-right px-4 py-2 font-medium">Delta</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {rows.map((row) => {
            const delta = row.valueB - row.valueA;
            return (
              <tr key={row.label}>
                <td
                  className={`px-4 py-2 ${
                    row.bold ? "font-semibold text-white" : "text-gray-400"
                  }`}
                >
                  {row.label}
                </td>
                <td className="text-right px-4 py-2 font-mono text-gray-300">
                  {formatCurrency(row.valueA)}
                </td>
                <td className="text-right px-4 py-2 font-mono text-gray-300">
                  {formatCurrency(row.valueB)}
                </td>
                <td
                  className={`text-right px-4 py-2 font-mono font-semibold ${
                    delta > 0 ? "text-green-400" : delta < 0 ? "text-red-400" : "text-gray-400"
                  }`}
                >
                  {delta > 0 ? "+" : ""}
                  {formatCurrency(delta)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

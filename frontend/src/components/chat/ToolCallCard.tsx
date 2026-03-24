"use client";

import { ToolCallInfo } from "@/lib/types";

const TOOL_LABELS: Record<string, string> = {
  calculate_vip_pl: "VIP Player P&L",
  calculate_vip_pl_comparison: "VIP Comparison",
  calculate_company_pl: "Company P&L",
  calculate_effective_bonus: "Effective Bonus Rate",
  calculate_vip_company_impact: "VIP Company Impact",
};

function formatArgs(args: Record<string, unknown>): string {
  const parts: string[] = [];
  for (const [key, value] of Object.entries(args)) {
    if (value !== null && value !== undefined) {
      if (typeof value === "object") {
        parts.push(`${key}: {...}`);
      } else {
        parts.push(`${key}: ${value}`);
      }
    }
  }
  return parts.join(", ");
}

export function ToolCallCard({ toolCall }: { toolCall: ToolCallInfo }) {
  const label = TOOL_LABELS[toolCall.name] || toolCall.name;
  const hasResult = !!toolCall.result;

  return (
    <div className="rounded-lg bg-gray-900 border border-gray-700 p-3 text-xs">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-blue-400 font-semibold">{label}</span>
        {hasResult ? (
          <span className="text-green-400">Done</span>
        ) : (
          <span className="text-yellow-400 animate-pulse">Running...</span>
        )}
      </div>
      <div className="text-gray-400 font-mono truncate">
        {formatArgs(toolCall.arguments)}
      </div>
    </div>
  );
}

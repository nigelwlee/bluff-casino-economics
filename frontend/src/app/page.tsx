"use client";

import { useChat } from "@/hooks/useChat";
import { useScenario } from "@/hooks/useScenario";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { VIPPLTable } from "@/components/results/PLTable";
import { ComparisonView } from "@/components/results/ComparisonView";
import { WaterfallChart } from "@/components/results/WaterfallChart";
import { ProjectionChart } from "@/components/results/ProjectionChart";
import { useState, useCallback } from "react";

function detectToolType(
  name: string
): "vip_pl" | "comparison" | "company_pl" | "effective_bonus" | "vip_impact" {
  if (name === "calculate_vip_pl_comparison") return "comparison";
  if (name === "calculate_company_pl") return "company_pl";
  if (name === "calculate_effective_bonus") return "effective_bonus";
  if (name === "calculate_vip_company_impact") return "vip_impact";
  return "vip_pl";
}

export default function Home() {
  const {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    currentToolCalls,
  } = useChat();
  const { scenario, save, isSaving } = useScenario();
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  // Collect all tool results from messages for the results panel
  const allToolResults = messages.flatMap(
    (m) =>
      m.toolCalls
        ?.filter((tc) => tc.result)
        .map((tc) => ({ name: tc.name, result: tc.result! })) || []
  );

  const latestResult = allToolResults[allToolResults.length - 1];

  const handleSave = useCallback(async () => {
    const calcResults = allToolResults.map((tr) => ({
      tool: tr.name,
      ...tr.result,
    }));
    const saved = await save("Scenario", messages, calcResults);
    const url = `${window.location.origin}/scenario/${saved.id}`;
    setShareUrl(url);
    navigator.clipboard.writeText(url);
  }, [allToolResults, messages, save]);

  return (
    <div className="flex h-screen">
      {/* Left: Chat Panel */}
      <div className="w-1/2 border-r border-gray-800 flex flex-col">
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          currentToolCalls={currentToolCalls}
          onSendMessage={sendMessage}
          onClear={clearMessages}
        />
      </div>

      {/* Right: Results Panel */}
      <div className="w-1/2 flex flex-col overflow-y-auto">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h2 className="text-lg font-semibold text-white">Results</h2>
          <div className="flex items-center gap-2">
            {shareUrl && (
              <span className="text-xs text-green-400">Link copied!</span>
            )}
            {allToolResults.length > 0 && (
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="text-xs text-gray-400 hover:text-white px-3 py-1.5 rounded border border-gray-700 hover:border-gray-500 disabled:opacity-50"
              >
                {isSaving ? "Saving..." : "Share"}
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 p-4 space-y-4">
          {!latestResult ? (
            <div className="flex items-center justify-center h-full text-gray-600 text-sm">
              Results will appear here when you ask a question
            </div>
          ) : (
            <>
              {allToolResults.map((tr, i) => {
                const type = detectToolType(tr.name);
                return (
                  <div key={i}>
                    {type === "vip_pl" && (
                      <>
                        <VIPPLTable result={tr.result} />
                        <div className="mt-4">
                          <WaterfallChart result={tr.result} />
                        </div>
                      </>
                    )}
                    {type === "comparison" && (
                      <ComparisonView result={tr.result} />
                    )}
                    {(type === "company_pl" || type === "vip_impact") && (
                      <ProjectionChart
                        result={
                          type === "vip_impact"
                            ? (tr.result as { projection: Record<string, unknown> })
                                .projection
                            : tr.result
                        }
                      />
                    )}
                    {type === "effective_bonus" && (
                      <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                        <h3 className="text-sm font-semibold text-white mb-2">
                          Effective Bonus Rate
                        </h3>
                        <div className="text-3xl font-bold text-red-400">
                          {(
                            ((tr.result as { effective_bonus_pct: number })
                              .effective_bonus_pct || 0) * 100
                          ).toFixed(2)}
                          % of GGR
                        </div>
                        <div className="text-sm text-gray-400 mt-1">
                          Total bonuses:{" "}
                          $
                          {Math.abs(
                            (tr.result as { total_bonuses: number })
                              .total_bonuses || 0
                          ).toLocaleString()}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

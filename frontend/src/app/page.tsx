"use client";

import { useState, useCallback, useMemo } from "react";
import { VIPConfigurator, CalculatorState } from "@/components/calculator/VIPConfigurator";
import { PLSummary } from "@/components/calculator/PLSummary";
import { useChat } from "@/hooks/useChat";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function Home() {
  const [calcState, setCalcState] = useState<CalculatorState | null>(null);
  const [breakevenVolumes, setBreakevenVolumes] = useState<{
    vipWagers: number;
    companyWagers: number;
  } | null>(null);

  // Convert CalculatorState to a plain dict for the chat hook
  const calcStateForChat = useMemo(
    () => (calcState ? (calcState as unknown as Record<string, unknown>) : null),
    [calcState]
  );

  const {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    currentToolCalls,
    sendFeedback,
  } = useChat(calcStateForChat);

  const handleCalcChange = useCallback((state: CalculatorState) => {
    setCalcState(state);
  }, []);

  const handleApplyBreakeven = useCallback((vipWagers: number, companyWagers: number) => {
    setBreakevenVolumes({ vipWagers, companyWagers });
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-3 shrink-0">
        <h1 className="text-lg font-bold text-white">Bluff Casino Economics</h1>
        <p className="text-xs text-gray-500">VIP Player P&L Calculator</p>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Calculator Inputs */}
        <div className="w-[380px] shrink-0 border-r border-gray-800 overflow-y-auto p-4">
          <VIPConfigurator
            onChange={handleCalcChange}
            externalVolumes={breakevenVolumes}
            onExternalApplied={() => setBreakevenVolumes(null)}
          />
        </div>

        {/* Center: P&L Results */}
        <div className="flex-1 overflow-y-auto p-5">
          <PLSummary state={calcState} onApplyBreakeven={handleApplyBreakeven} />
        </div>

        {/* Right: AI Chat (1/3 of window) */}
        <div className="w-1/3 shrink-0 border-l border-gray-800 flex flex-col">
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            currentToolCalls={currentToolCalls}
            onSendMessage={sendMessage}
            onClear={clearMessages}
            onFeedback={sendFeedback}
          />
        </div>
      </div>
    </div>
  );
}

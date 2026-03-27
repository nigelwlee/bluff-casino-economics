"use client";

import { useState, useCallback, useMemo } from "react";
import { VIPConfigurator, CalculatorState } from "@/components/calculator/VIPConfigurator";
import { PLSummary } from "@/components/calculator/PLSummary";
import { useChat } from "@/hooks/useChat";
import { ChatPanel } from "@/components/chat/ChatPanel";

type MobileTab = "inputs" | "results" | "chat";

export default function Home() {
  const [calcState, setCalcState] = useState<CalculatorState | null>(null);
  const [breakevenVolumes, setBreakevenVolumes] = useState<{
    vipWagers: number;
    companyWagers: number;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<MobileTab>("inputs");

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

  const tabClass = (tab: MobileTab) =>
    `flex-1 py-2.5 text-sm font-medium text-center transition-colors ${
      activeTab === tab
        ? "text-white border-b-2 border-blue-500"
        : "text-gray-400 border-b-2 border-transparent"
    }`;

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-3 shrink-0">
        <h1 className="text-lg font-bold text-white">Bluff Casino Economics</h1>
        <p className="text-xs text-gray-500">VIP Player P&L Calculator</p>
      </header>

      {/* Mobile Tab Bar */}
      <div className="lg:hidden flex border-b border-gray-800 shrink-0">
        <button className={tabClass("inputs")} onClick={() => setActiveTab("inputs")}>
          Calculator
        </button>
        <button className={tabClass("results")} onClick={() => setActiveTab("results")}>
          Results
        </button>
        <button className={tabClass("chat")} onClick={() => setActiveTab("chat")}>
          Chat
        </button>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Calculator Inputs */}
        <div
          className={`${
            activeTab === "inputs" ? "flex flex-col w-full" : "hidden"
          } lg:flex lg:flex-col lg:w-[380px] lg:shrink-0 border-r border-gray-800 overflow-y-auto p-4`}
        >
          <VIPConfigurator
            onChange={handleCalcChange}
            externalVolumes={breakevenVolumes}
            onExternalApplied={() => setBreakevenVolumes(null)}
          />
        </div>

        {/* Center: P&L Results */}
        <div
          className={`${
            activeTab === "results" ? "flex flex-col w-full" : "hidden"
          } lg:flex lg:flex-col lg:flex-1 overflow-y-auto p-5`}
        >
          <PLSummary state={calcState} onApplyBreakeven={handleApplyBreakeven} />
        </div>

        {/* Right: AI Chat (1/3 of window) */}
        <div
          className={`${
            activeTab === "chat" ? "flex flex-col w-full" : "hidden"
          } lg:flex lg:flex-col lg:w-1/3 lg:shrink-0 border-l border-gray-800`}
        >
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

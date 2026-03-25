"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";
import { ToolCallCard } from "./ToolCallCard";
import { ToolCallInfo } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
  currentToolCalls: ToolCallInfo[];
  onSendMessage: (message: string) => void;
  onClear: () => void;
  onFeedback?: (note?: string) => Promise<{ id: number; status: string }>;
}

const EXAMPLE_QUESTIONS = [
  "What's the Whale P&L with current defaults?",
  "What if we give 10% lossback to Dolphins instead of 30%?",
  "Show me 12-month P&L at $100M monthly wagers",
  "If 80% of volume is Whales with 55% bonus rate, when do we break even?",
];

export function ChatPanel({
  messages,
  isLoading,
  currentToolCalls,
  onSendMessage,
  onClear,
  onFeedback,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedbackNote, setFeedbackNote] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState<"idle" | "sending" | "sent">("idle");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentToolCalls]);

  // Auto-hide feedback confirmation after 3s
  useEffect(() => {
    if (feedbackStatus === "sent") {
      const timer = setTimeout(() => {
        setFeedbackStatus("idle");
        setShowFeedbackInput(false);
        setFeedbackNote("");
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [feedbackStatus]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleFeedbackSubmit = async () => {
    if (!onFeedback) return;
    setFeedbackStatus("sending");
    try {
      await onFeedback(feedbackNote || undefined);
      setFeedbackStatus("sent");
    } catch {
      setFeedbackStatus("idle");
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">
          Bluff Economics Agent
        </h2>
        {messages.length > 0 && (
          <button
            onClick={onClear}
            className="text-xs text-gray-400 hover:text-white px-2 py-1 rounded border border-gray-700 hover:border-gray-500"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h3 className="text-xl font-semibold text-gray-300 mb-2">
              Ask about casino economics
            </h3>
            <p className="text-gray-500 text-sm mb-6 max-w-sm">
              I can calculate VIP P&L, compare deals, project company revenue,
              and more.
            </p>
            <div className="grid gap-2 w-full max-w-md">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => onSendMessage(q)}
                  className="text-left text-sm px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-gray-300 hover:bg-gray-750 hover:border-gray-600 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {isLoading && currentToolCalls.length > 0 && (
              <div className="mb-4 space-y-2 ml-2">
                {currentToolCalls.map((tc, i) => (
                  <ToolCallCard key={i} toolCall={tc} />
                ))}
              </div>
            )}
            {isLoading && currentToolCalls.length === 0 && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                    <span
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <span
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Feedback section */}
            {messages.length > 0 && !isLoading && onFeedback && (
              <div className="mt-2 mb-4">
                {feedbackStatus === "sent" ? (
                  <p className="text-xs text-amber-400">Feedback recorded — thank you.</p>
                ) : showFeedbackInput ? (
                  <div className="flex flex-col gap-2">
                    <input
                      type="text"
                      value={feedbackNote}
                      onChange={(e) => setFeedbackNote(e.target.value)}
                      placeholder="What felt wrong? (optional)"
                      className="bg-gray-800 border border-amber-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleFeedbackSubmit}
                        disabled={feedbackStatus === "sending"}
                        className="text-xs px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-700 text-white disabled:opacity-50 transition-colors"
                      >
                        {feedbackStatus === "sending" ? "Sending..." : "Submit"}
                      </button>
                      <button
                        onClick={() => {
                          setShowFeedbackInput(false);
                          setFeedbackNote("");
                        }}
                        className="text-xs px-3 py-1.5 rounded border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowFeedbackInput(true)}
                    className="text-xs text-amber-500 hover:text-amber-400 transition-colors"
                  >
                    Something feels wrong
                  </button>
                )}
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="px-4 py-3 border-t border-gray-800"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about VIP deals, P&L projections, breakeven..."
            disabled={isLoading}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white px-5 py-3 rounded-xl text-sm font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

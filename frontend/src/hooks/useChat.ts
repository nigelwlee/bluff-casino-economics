"use client";

import { useState, useCallback, useRef } from "react";
import { ChatMessage, ToolCallInfo } from "@/lib/types";
import { connectChat, submitFeedback } from "@/lib/api";

export function useChat(calculatorState?: Record<string, unknown> | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentToolCalls, setCurrentToolCalls] = useState<ToolCallInfo[]>([]);
  const cancelRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    (content: string) => {
      const userMessage: ChatMessage = { role: "user", content };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setCurrentToolCalls([]);

      let assistantText = "";
      const toolCalls: ToolCallInfo[] = [];

      const cancel = connectChat(
        content,
        messages,
        {
          onText: (text) => {
            assistantText += text;
            setMessages((prev) => {
              const updated = [...prev];
              const lastIdx = updated.length - 1;
              if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
                updated[lastIdx] = {
                  ...updated[lastIdx],
                  content: assistantText,
                };
              } else {
                updated.push({
                  role: "assistant",
                  content: assistantText,
                  toolCalls,
                });
              }
              return updated;
            });
          },
          onToolStart: (name, args) => {
            const tc: ToolCallInfo = { name, arguments: args };
            toolCalls.push(tc);
            setCurrentToolCalls([...toolCalls]);
          },
          onToolResult: (name, result) => {
            const tc = toolCalls.find(
              (t) => t.name === name && !t.result
            );
            if (tc) tc.result = result;
            setCurrentToolCalls([...toolCalls]);
          },
          onDone: () => {
            setIsLoading(false);
            setMessages((prev) => {
              const updated = [...prev];
              const lastIdx = updated.length - 1;
              if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
                updated[lastIdx] = {
                  ...updated[lastIdx],
                  content: assistantText,
                  toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
                };
              } else if (assistantText || toolCalls.length > 0) {
                updated.push({
                  role: "assistant",
                  content: assistantText,
                  toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
                });
              }
              return updated;
            });
            setCurrentToolCalls([]);
          },
          onError: (error) => {
            setIsLoading(false);
            setMessages((prev) => [
              ...prev,
              { role: "assistant", content: `Error: ${error}` },
            ]);
          },
        },
        calculatorState
      );

      cancelRef.current = cancel;
    },
    [messages, calculatorState]
  );

  const cancel = useCallback(() => {
    cancelRef.current?.();
    setIsLoading(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentToolCalls([]);
  }, []);

  const sendFeedback = useCallback(
    async (note?: string) => {
      return submitFeedback(calculatorState ?? null, messages, note);
    },
    [calculatorState, messages]
  );

  return {
    messages,
    setMessages,
    isLoading,
    sendMessage,
    cancel,
    clearMessages,
    currentToolCalls,
    sendFeedback,
  };
}

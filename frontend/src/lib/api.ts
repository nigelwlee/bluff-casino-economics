import { ChatMessage, Scenario } from "./types";

const API_BASE = "/api";

export async function streamChat(
  message: string,
  history: ChatMessage[],
  onText: (text: string) => void,
  onToolStart: (name: string, args: Record<string, unknown>) => void,
  onToolResult: (name: string, result: Record<string, unknown>) => void,
  onDone: () => void,
  onError: (error: string) => void
) {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history: history.map((m) => ({ role: m.role, content: m.content })),
      }),
    });

    if (!response.ok) {
      onError(`Server error: ${response.status}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError("No response body");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          const eventType = line.slice(7).trim();
          continue;
        }
        if (line.startsWith("data: ")) {
          const data = JSON.parse(line.slice(6));
          // Need to track the event type from the previous line
          // SSE format sends event: X then data: Y
        }
      }
    }

    // Simpler approach: parse SSE manually
    onDone();
  } catch (err) {
    onError(err instanceof Error ? err.message : "Unknown error");
  }
}

// Simpler SSE parser using EventSource-like approach
export function connectChat(
  message: string,
  history: ChatMessage[],
  callbacks: {
    onText: (text: string) => void;
    onToolStart: (name: string, args: Record<string, unknown>) => void;
    onToolResult: (name: string, result: Record<string, unknown>) => void;
    onDone: () => void;
    onError: (error: string) => void;
  },
  calculatorState?: Record<string, unknown> | null
) {
  const abortController = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          history: history.map((m) => ({ role: m.role, content: m.content })),
          calculator_state: calculatorState ?? null,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        callbacks.onError(`Server error: ${response.status}`);
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";
      let currentEvent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              switch (currentEvent) {
                case "text":
                  callbacks.onText(data.content);
                  break;
                case "tool_start":
                  callbacks.onToolStart(data.name, data.arguments);
                  break;
                case "tool_result":
                  callbacks.onToolResult(data.name, data.result);
                  break;
                case "done":
                  callbacks.onDone();
                  break;
                case "tool_error":
                  callbacks.onError(`Tool error: ${data.error}`);
                  break;
              }
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }

      callbacks.onDone();
    } catch (err) {
      if (!abortController.signal.aborted) {
        callbacks.onError(err instanceof Error ? err.message : "Unknown error");
      }
    }
  })();

  return () => abortController.abort();
}

export async function saveScenario(
  name: string,
  chatHistory: ChatMessage[],
  calcResults: Record<string, unknown>[]
): Promise<Scenario> {
  const response = await fetch(`${API_BASE}/scenarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      chat_history: chatHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      calc_results: calcResults,
    }),
  });
  return response.json();
}

export async function loadScenario(id: string): Promise<Scenario> {
  const response = await fetch(`${API_BASE}/scenarios/${id}`);
  if (!response.ok) throw new Error("Scenario not found");
  return response.json();
}

export async function submitFeedback(
  calculatorState: Record<string, unknown> | null,
  chatHistory: ChatMessage[],
  userNote?: string
): Promise<{ id: number; status: string }> {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      calculator_state: calculatorState,
      chat_history: chatHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      user_note: userNote || null,
    }),
  });
  return response.json();
}

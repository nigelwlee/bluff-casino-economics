"use client";

import { useState, useCallback } from "react";
import { ChatMessage, Scenario } from "@/lib/types";
import { saveScenario, loadScenario } from "@/lib/api";

export function useScenario() {
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const save = useCallback(
    async (
      name: string,
      chatHistory: ChatMessage[],
      calcResults: Record<string, unknown>[]
    ) => {
      setIsSaving(true);
      try {
        const saved = await saveScenario(name, chatHistory, calcResults);
        setScenario(saved);
        return saved;
      } finally {
        setIsSaving(false);
      }
    },
    []
  );

  const load = useCallback(async (id: string) => {
    const loaded = await loadScenario(id);
    setScenario(loaded);
    return loaded;
  }, []);

  return { scenario, save, load, isSaving };
}

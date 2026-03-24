"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Scenario } from "@/lib/types";
import { loadScenario } from "@/lib/api";
import { MessageBubble } from "@/components/chat/MessageBubble";

export default function ScenarioPage() {
  const params = useParams();
  const id = params.id as string;
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScenario(id)
      .then(setScenario)
      .catch(() => setError("Scenario not found"));
  }, [id]);

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen text-red-400">
        {error}
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-500">
        Loading...
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">{scenario.name}</h1>
        <p className="text-sm text-gray-500">
          Created: {new Date(scenario.created_at).toLocaleString()}
        </p>
      </div>
      <div className="space-y-4">
        {scenario.chat_history.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
      </div>
    </div>
  );
}

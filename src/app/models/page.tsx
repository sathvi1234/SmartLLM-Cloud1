"use client";

import React, { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, Loader2, AlertTriangle } from "lucide-react";
import { api, ApiError, ModelInfo } from "@/lib/api";

const PROVIDER_LABELS: Record<string, string> = {
  openai: "OpenAI",
  gemini: "Google Gemini",
  groq: "Groq",
  xai: "xAI / Grok",
  ollama: "Ollama (Local)",
};

export default function ModelsPage() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.models()
      .then((d) => setModels(d.models))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load models."))
      .finally(() => setLoading(false));
  }, []);

  const providers = Array.from(new Set(models.map((m) => m.provider)));

  return (
    <DashboardLayout activeItem="models">
      <Header title="Models" subtitle="Router catalog with official pricing" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        {loading && (
          <div className="h-[300px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
          </div>
        )}

        {error && !loading && (
          <AnimatedCard className="p-6 border-red-500/20 bg-red-500/5 text-center">
            <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-red-400 mb-1">Could not load models</p>
            <p className="text-sm text-red-300/70">{error}</p>
          </AnimatedCard>
        )}

        {!loading && !error && providers.map((provider, pi) => {
          const providerModels = models.filter((m) => m.provider === provider);
          const anyAvailable = providerModels.some((m) => m.available);
          const configured = providerModels.some((m) => m.configured);
          return (
            <AnimatedCard key={provider} delay={pi * 0.05} padding="none">
              <div className="flex items-center justify-between gap-3 p-5 pb-3">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-violet-400" />
                  <h3 className="text-sm font-semibold text-white">{PROVIDER_LABELS[provider] ?? provider}</h3>
                </div>
                <Badge variant={anyAvailable ? "success" : configured ? "warning" : "neutral"} dot>
                  {anyAvailable ? "Available" : configured ? "Configured, unreachable" : "Not configured"}
                </Badge>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/[0.06] text-[10px] text-white/25 uppercase tracking-widest">
                      <th className="text-left font-semibold py-2 px-5">Model</th>
                      <th className="text-right font-semibold py-2 px-5">Input $/1M</th>
                      <th className="text-right font-semibold py-2 px-5">Output $/1M</th>
                      <th className="text-right font-semibold py-2 px-5">Capability</th>
                      <th className="text-right font-semibold py-2 px-5">Context</th>
                      <th className="text-right font-semibold py-2 px-5">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerModels.map((m) => (
                      <tr key={m.model} className="border-b border-white/[0.04] last:border-0 hover:bg-white/[0.02]">
                        <td className="py-3 px-5 font-mono text-white/85">{m.model}</td>
                        <td className="py-3 px-5 text-right font-mono text-white/60">
                          {m.input_price_per_1m === 0 ? "Free (local)" : `$${m.input_price_per_1m.toFixed(2)}`}
                        </td>
                        <td className="py-3 px-5 text-right font-mono text-white/60">
                          {m.output_price_per_1m === 0 ? "Free (local)" : `$${m.output_price_per_1m.toFixed(2)}`}
                        </td>
                        <td className="py-3 px-5 text-right text-white/60">{m.capability_score}/10</td>
                        <td className="py-3 px-5 text-right text-white/60">{(m.context_limit / 1000).toFixed(0)}K</td>
                        <td className="py-3 px-5 text-right">
                          <Badge variant={m.available ? "success" : "neutral"}>
                            {m.available ? "Available" : "Unavailable"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </AnimatedCard>
          );
        })}

        {!loading && !error && (
          <p className="text-[11px] text-white/30">
            Pricing shown is the official per-1M-token rate from the centralized model catalog and is used for all
            cost calculations. Local Ollama models incur no token cost.
          </p>
        )}
      </main>
    </DashboardLayout>
  );
}

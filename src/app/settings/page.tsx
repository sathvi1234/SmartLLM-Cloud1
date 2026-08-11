"use client";

import React, { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Shield, Server, AlertTriangle, RefreshCw } from "lucide-react";
import { api, API_BASE, ApiError, ProviderStatus } from "@/lib/api";

const PROVIDER_LABELS: Record<string, string> = {
  openai: "OpenAI",
  gemini: "Google Gemini",
  groq: "Groq",
  xai: "xAI / Grok",
  ollama: "Ollama (Local)",
};

const KEY_NAMES: Record<string, string> = {
  openai: "OPENAI_API_KEY",
  gemini: "GEMINI_API_KEY",
  groq: "GROQ_API_KEY",
  xai: "XAI_API_KEY",
  ollama: "OLLAMA_BASE_URL",
};

export default function SettingsPage() {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    api.providers()
      .then(setProviders)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load provider status."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  return (
    <DashboardLayout activeItem="settings">
      <Header title="Settings" subtitle="Provider health & configuration" />

      <main className="flex-1 p-6 space-y-6 max-w-[1200px] mx-auto w-full">
        <AnimatedCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-violet-400" />
              <h3 className="text-sm font-semibold text-white">Provider Health</h3>
            </div>
            <button
              onClick={load}
              className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
          </div>

          {loading && (
            <div className="h-32 flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
            </div>
          )}

          {error && !loading && (
            <div className="p-4 rounded-lg border border-red-500/20 bg-red-500/5 flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
              <p className="text-sm text-red-300/80">{error}</p>
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-2">
              {providers.map((p) => (
                <div
                  key={p.name}
                  className="flex items-center justify-between gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]"
                >
                  <div>
                    <p className="text-sm font-medium text-white/85">{PROVIDER_LABELS[p.name] ?? p.name}</p>
                    <p className="text-[11px] text-white/30 font-mono">{KEY_NAMES[p.name]} (backend .env)</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={p.configured ? "info" : "neutral"}>
                      {p.configured ? "Configured" : "Not configured"}
                    </Badge>
                    <Badge variant={p.available ? "success" : "error"} dot>
                      {p.available ? "Available" : "Unavailable"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </AnimatedCard>

        <AnimatedCard className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Security</h3>
          </div>
          <ul className="text-sm text-white/50 space-y-2 list-disc pl-5">
            <li>Provider API keys live only in the backend <span className="font-mono text-white/70">.env</span> file and are never sent to the browser.</li>
            <li>This page only shows whether a key is configured — never the key itself.</li>
            <li><span className="font-mono text-white/70">.env</span> files are excluded from git via <span className="font-mono text-white/70">.gitignore</span>.</li>
          </ul>
        </AnimatedCard>

        <AnimatedCard className="p-5">
          <h3 className="text-sm font-semibold text-white mb-3">Connection</h3>
          <div className="text-sm text-white/50 space-y-1">
            <p>Backend API base: <span className="font-mono text-white/70">{API_BASE}</span></p>
            <p className="text-[11px] text-white/30">
              Configure via <span className="font-mono">NEXT_PUBLIC_API_URL</span> (frontend) — this is a public URL, not a secret.
            </p>
          </div>
        </AnimatedCard>
      </main>
    </DashboardLayout>
  );
}

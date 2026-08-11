"use client";

import React, { useEffect, useMemo, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Bot, Terminal, Loader2, Wand2, Route, Gauge, Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  api, ApiError, formatCost, ModelInfo, SmartGenerationResult,
} from "@/lib/api";

const MODES = [
  { id: "cost", label: "Cost", description: "Cheapest suitable model" },
  { id: "speed", label: "Speed", description: "Fastest provider/model" },
  { id: "balanced", label: "Balanced", description: "Weighted cost/speed/quality" },
  { id: "quality", label: "Quality", description: "Highest-capability model" },
];

function Stat({ label, value, sub }: { label: string; value: React.ReactNode; sub?: string }) {
  return (
    <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-3">
      <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">{label}</p>
      <p className="text-sm font-semibold text-white break-words">{value}</p>
      {sub && <p className="text-[10px] text-white/30 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function PlaygroundPage() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("balanced");
  const [provider, setProvider] = useState("auto");
  const [model, setModel] = useState("");
  const [optimize, setOptimize] = useState(true);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SmartGenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.models()
      .then((data) => {
        setModels(data.models);
        // Prefer Groq for live testing when it is configured; keep Auto otherwise.
        const groq = data.models.find((m) => m.provider === "groq" && m.available);
        if (groq) {
          setProvider("groq");
          setModel(groq.model);
        }
      })
      .catch(() => setModels([]));
  }, []);

  const providerModels = useMemo(
    () => models.filter((m) => m.provider === provider && (provider === "auto" || m.available !== false)),
    [models, provider]
  );

  useEffect(() => {
    if (provider !== "auto") {
      setModel((prev) =>
        providerModels.some((m) => m.model === prev) ? prev : providerModels[0]?.model ?? ""
      );
    }
  }, [provider, providerModels]);

  const run = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.smartGenerate({
        prompt,
        mode,
        provider,
        model_name: provider === "auto" ? undefined : model || undefined,
        optimize,
        source: "playground",
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const opt = result?.optimization;

  return (
    <DashboardLayout activeItem="playground">
      <Header title="Playground" subtitle="Analyze → Optimize → Route → Generate" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Section */}
          <div className="lg:col-span-1 space-y-4">
            <AnimatedCard className="p-4 flex flex-col">
              <div className="flex items-center gap-2 mb-4">
                <Terminal className="w-5 h-5 text-violet-400" />
                <h3 className="font-semibold text-white">SmartLLM Request</h3>
              </div>

              <div className="space-y-4 flex-1 flex flex-col">
                <div>
                  <label className="text-xs text-white/40 mb-1.5 block">Optimization Mode</label>
                  <div className="grid grid-cols-2 gap-2">
                    {MODES.map((m) => (
                      <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        className={cn(
                          "text-left rounded-lg border p-2 transition-colors",
                          mode === m.id
                            ? "border-violet-500/60 bg-violet-500/10 text-white"
                            : "border-white/10 bg-[#0F0F1A] text-white/50 hover:border-white/25"
                        )}
                      >
                        <span className="text-xs font-semibold block">{m.label}</span>
                        <span className="text-[10px] text-white/35">{m.description}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-white/40 mb-1 block">Provider</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-violet-500"
                  >
                    <option value="auto">Auto (SmartLLM Router)</option>
                    <option value="openai">OpenAI</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="groq">Groq</option>
                    <option value="xai">xAI / Grok</option>
                    <option value="ollama">Ollama (Local)</option>
                  </select>
                </div>

                {provider !== "auto" && (
                  <div>
                    <label className="text-xs text-white/40 mb-1 block">Model</label>
                    {providerModels.length > 0 ? (
                      <select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-violet-500"
                      >
                        {providerModels.map((m) => (
                          <option key={m.model} value={m.model}>{m.model}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-violet-500"
                        placeholder="e.g. gpt-4o-mini"
                      />
                    )}
                  </div>
                )}

                <label className="flex items-center justify-between gap-2 bg-[#0F0F1A] border border-white/10 rounded-lg p-2.5 cursor-pointer">
                  <span className="text-xs text-white/60 flex items-center gap-2">
                    <Wand2 className="w-3.5 h-3.5 text-emerald-400" />
                    Safe prompt optimization
                  </span>
                  <input
                    type="checkbox"
                    checked={optimize}
                    onChange={(e) => setOptimize(e.target.checked)}
                    className="accent-violet-500 w-4 h-4"
                  />
                </label>

                <div className="flex-1 flex flex-col">
                  <label className="text-xs text-white/40 mb-1 block">Prompt</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={7}
                    className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-violet-500 resize-none font-mono"
                    placeholder="e.g. Write a Python function to find duplicate elements in a list."
                  />
                </div>

                <button
                  onClick={run}
                  disabled={loading || !prompt.trim()}
                  className="w-full py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:hover:bg-violet-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                  {loading ? "Processing..." : "Run SmartLLM"}
                </button>
              </div>
            </AnimatedCard>
          </div>

          {/* Output Section */}
          <div className="lg:col-span-2 space-y-4">
            {error && (
              <AnimatedCard className="p-4 border-red-500/20 bg-red-500/5">
                <p className="text-sm font-semibold text-red-400 mb-1">Request failed</p>
                <p className="text-sm text-red-300/80">{error}</p>
              </AnimatedCard>
            )}

            {!result && !loading && !error && (
              <div className="h-[500px] flex flex-col items-center justify-center border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
                <Bot className="w-12 h-12 text-white/20 mb-3" />
                <p className="text-white/40 text-sm">Enter a prompt and run SmartLLM to see results.</p>
              </div>
            )}

            {loading && (
              <div className="h-[500px] flex flex-col items-center justify-center border border-white/5 rounded-2xl bg-white/[0.02]">
                <Loader2 className="w-10 h-10 text-violet-500 animate-spin mb-4" />
                <p className="text-violet-400/60 text-sm">Analyzing, optimizing and routing your request...</p>
              </div>
            )}

            {result && (
              <>
                {/* Routing */}
                <AnimatedCard className="p-4 border-violet-500/20 bg-violet-500/5">
                  <div className="flex items-center gap-2 mb-3">
                    <Route className="w-4 h-4 text-violet-400" />
                    <h3 className="text-sm font-semibold text-white">Routing Decision</h3>
                    <Badge variant={result.routing.auto_routed ? "default" : "neutral"}>
                      {result.routing.auto_routed ? "Auto-routed" : "Manual"}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-3">
                    <Stat label="Provider" value={result.provider} />
                    <Stat label="Model" value={result.model} />
                    <Stat label="Mode" value={result.routing.mode} />
                  </div>
                  <p className="text-xs text-white/60 leading-relaxed">{result.routing.reason}</p>
                </AnimatedCard>

                {/* Usage / Performance / Cost */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <Stat label="Input Tokens" value={result.usage.prompt_tokens} sub="actual provider usage" />
                  <Stat label="Output Tokens" value={result.usage.completion_tokens} sub="actual provider usage" />
                  <Stat label="Total Tokens" value={result.usage.total_tokens} />
                  <Stat label="Latency" value={`${Math.round(result.latency_ms)} ms`} sub="measured server-side" />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <Stat
                    label="Input Cost"
                    value={formatCost(result.cost.input_cost_usd, result.cost.pricing_available)}
                  />
                  <Stat
                    label="Output Cost"
                    value={formatCost(result.cost.output_cost_usd, result.cost.pricing_available)}
                  />
                  <Stat
                    label="Total Cost"
                    value={formatCost(result.cost.total_cost_usd, result.cost.pricing_available)}
                    sub={result.cost.pricing_available ? result.cost.pricing_note : undefined}
                  />
                </div>

                {/* Response */}
                <AnimatedCard className="p-4 min-h-[200px]">
                  <div className="flex items-center gap-2 mb-3 border-b border-white/10 pb-2">
                    <Bot className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-semibold text-white/80">Response</h3>
                  </div>
                  <div className="max-w-none text-sm text-white/80 font-mono whitespace-pre-wrap">
                    {result.content}
                  </div>
                </AnimatedCard>

                {/* Optimization */}
                {opt && (
                  <AnimatedCard className={cn("p-4", opt.optimization_applied ? "border-emerald-500/20 bg-emerald-500/5" : "border-white/10")}>
                    <div className="flex items-center gap-2 mb-3">
                      <Wand2 className="w-4 h-4 text-emerald-400" />
                      <h3 className="text-sm font-semibold text-white">Prompt Optimization</h3>
                      <Badge variant={opt.optimization_applied ? "success" : "neutral"}>
                        {opt.optimization_applied ? `-${opt.reduction_percent}% est. tokens` : "No safe reductions found"}
                      </Badge>
                    </div>
                    {opt.optimization_applied ? (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                          <div>
                            <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">
                              Original ({opt.estimated_tokens_before} est. tokens)
                            </p>
                            <div className="text-xs text-white/60 font-mono bg-black/20 p-3 rounded whitespace-pre-wrap">
                              {opt.original_prompt}
                            </div>
                          </div>
                          <div>
                            <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">
                              Optimized ({opt.estimated_tokens_after} est. tokens)
                            </p>
                            <div className="text-xs text-emerald-200/80 font-mono bg-black/20 p-3 rounded whitespace-pre-wrap">
                              {opt.optimized_prompt}
                            </div>
                          </div>
                        </div>
                        <p className="text-[11px] text-white/40">
                          Techniques: {opt.techniques_applied.join(", ") || "none"} · {opt.note}
                        </p>
                      </>
                    ) : (
                      <p className="text-xs text-white/50">{opt.note}</p>
                    )}
                  </AnimatedCard>
                )}

                {/* Analysis */}
                <AnimatedCard className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Gauge className="w-4 h-4 text-blue-400" />
                    <h3 className="text-sm font-semibold text-white">Request Analysis</h3>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <Stat label="Intent" value={result.analysis.intent.join(", ")} />
                    <Stat label="Difficulty" value={result.analysis.difficulty} />
                    <Stat label="Complexity" value={`${result.analysis.complexity}/10`} />
                    <Stat label="Est. Prompt Tokens" value={result.analysis.estimated_tokens} sub="tokenizer estimate" />
                  </div>
                </AnimatedCard>
              </>
            )}
          </div>
        </div>
      </main>
    </DashboardLayout>
  );
}

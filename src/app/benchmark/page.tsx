"use client";

import React, { useEffect, useMemo, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  LineChart, Loader2, CheckCircle2, HelpCircle, Route, ListChecks,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  api, ApiError, BenchmarkResult, formatCost, formatPct, ModelInfo,
} from "@/lib/api";

const SUITE_PROMPTS: { category: string; prompt: string }[] = [
  { category: "Coding", prompt: "Write a Python function to find duplicate elements in a list." },
  { category: "Coding", prompt: "Write a JavaScript function that debounces another function." },
  { category: "Explanation", prompt: "Explain how HTTPS encryption works in simple terms." },
  { category: "Summarization", prompt: "Summarize the key trade-offs between SQL and NoSQL databases in a short paragraph." },
  { category: "SQL", prompt: "Write a SQL query that returns the top 5 customers by total order value from tables customers(id, name) and orders(id, customer_id, total)." },
  { category: "Reasoning", prompt: "A farmer has 17 sheep. All but 9 run away. How many sheep are left? Explain your reasoning." },
  { category: "Short response", prompt: "What is the capital of Japan? One word answer." },
  { category: "Short response", prompt: "Is the number 97 prime? Answer yes or no with one sentence of justification." },
  { category: "Long response", prompt: "Write a detailed step-by-step guide for deploying a web application with Docker, covering images, containers, networking and volumes." },
  { category: "Explanation", prompt: "Explain the difference between processes and threads, including when to use each." },
];

interface SuiteRow {
  category: string;
  prompt: string;
  status: "pending" | "running" | "done" | "error";
  result?: BenchmarkResult;
  error?: string;
}

function MetricRow({
  label, direct, smart, format, lowerIsBetter = true,
}: {
  label: string;
  direct: number | null;
  smart: number | null;
  format: (v: number) => string;
  lowerIsBetter?: boolean;
}) {
  const winner = (mine: number | null, other: number | null) => {
    if (mine === null || other === null || mine === other) return "text-white/70";
    const won = lowerIsBetter ? mine < other : mine > other;
    return won ? "text-emerald-400 font-bold" : "text-white/50";
  };
  return (
    <div className="grid grid-cols-3 items-center py-2 border-b border-white/5 text-sm">
      <span className="text-white/40">{label}</span>
      <span className={cn("font-mono text-right pr-6", winner(direct, smart))}>
        {direct === null ? "Pricing unavailable" : format(direct)}
      </span>
      <span className={cn("font-mono text-right", winner(smart, direct))}>
        {smart === null ? "Pricing unavailable" : format(smart)}
      </span>
    </div>
  );
}

const PROVIDER_LABELS: Record<string, string> = {
  openai: "OpenAI",
  gemini: "Google Gemini",
  groq: "Groq",
  xai: "xAI / Grok",
  ollama: "Ollama (Local)",
};

/** Prefer OpenAI, then Groq (primary live test path), then other configured providers. */
function pickDefaultBaseline(models: ModelInfo[]): { provider: string; model: string } | null {
  const available = models.filter((m) => m.available);
  if (available.length === 0) return null;
  const order = ["openai", "groq", "xai", "gemini", "ollama"];
  for (const provider of order) {
    const match = available.find((m) => m.provider === provider);
    if (match) return { provider: match.provider, model: match.model };
  }
  return { provider: available[0].provider, model: available[0].model };
}

export default function BenchmarkPage() {
  const [prompt, setPrompt] = useState("Write a Python function to find duplicate elements in a list.");
  const [baselineProvider, setBaselineProvider] = useState("");
  const [baselineModel, setBaselineModel] = useState("");
  const [mode, setMode] = useState("balanced");
  const [optimize, setOptimize] = useState(true);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BenchmarkResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showFormulas, setShowFormulas] = useState(false);

  const [suite, setSuite] = useState<SuiteRow[]>(SUITE_PROMPTS.map((p) => ({ ...p, status: "pending" })));
  const [suiteRunning, setSuiteRunning] = useState(false);

  useEffect(() => {
    api.models()
      .then((d) => {
        setModels(d.models);
        const pick = pickDefaultBaseline(d.models);
        if (pick) {
          setBaselineProvider(pick.provider);
          setBaselineModel(pick.model);
        }
      })
      .catch(() => setModels([]))
      .finally(() => setModelsLoaded(true));
  }, []);

  const availableProviders = useMemo(() => {
    const names = Array.from(new Set(models.filter((m) => m.available).map((m) => m.provider)));
    // Keep a stable order matching the catalog preference
    const order = ["openai", "groq", "xai", "gemini", "ollama"];
    return names.sort((a, b) => order.indexOf(a) - order.indexOf(b));
  }, [models]);

  const baselineModels = useMemo(
    () => models.filter((m) => m.provider === baselineProvider && m.available),
    [models, baselineProvider]
  );

  useEffect(() => {
    if (!baselineProvider && availableProviders.length > 0) {
      const pick = pickDefaultBaseline(models);
      if (pick) setBaselineProvider(pick.provider);
      return;
    }
    if (baselineProvider && availableProviders.length > 0 && !availableProviders.includes(baselineProvider)) {
      const pick = pickDefaultBaseline(models);
      if (pick) {
        setBaselineProvider(pick.provider);
        setBaselineModel(pick.model);
      }
    }
  }, [availableProviders, baselineProvider, models]);

  useEffect(() => {
    setBaselineModel((prev) =>
      baselineModels.some((m) => m.model === prev) ? prev : baselineModels[0]?.model ?? ""
    );
  }, [baselineModels]);

  const baselineReady = Boolean(baselineProvider && baselineModel);
  const baselineLabel = baselineReady
    ? `${PROVIDER_LABELS[baselineProvider] ?? baselineProvider} / ${baselineModel}`
    : "No configured provider";

  const run = async () => {
    if (!prompt.trim() || !baselineReady) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.benchmark({
        prompt,
        baseline_provider: baselineProvider,
        baseline_model: baselineModel,
        mode,
        optimize,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const runSuite = async () => {
    if (suiteRunning || !baselineReady) return;
    setSuiteRunning(true);
    const rows: SuiteRow[] = SUITE_PROMPTS.map((p) => ({ ...p, status: "pending" }));
    setSuite([...rows]);
    for (let i = 0; i < rows.length; i++) {
      rows[i] = { ...rows[i], status: "running" };
      setSuite([...rows]);
      try {
        const res = await api.benchmark({
          prompt: rows[i].prompt,
          baseline_provider: baselineProvider,
          baseline_model: baselineModel,
          mode,
          optimize,
        });
        rows[i] = { ...rows[i], status: "done", result: res };
      } catch (err) {
        rows[i] = { ...rows[i], status: "error", error: err instanceof ApiError ? err.message : "Failed" };
      }
      setSuite([...rows]);
    }
    setSuiteRunning(false);
  };

  const suiteDone = suite.filter((r) => r.status === "done");
  const suiteAgg = useMemo(() => {
    if (suiteDone.length === 0) return null;
    const avg = (vals: (number | null)[]) => {
      const nums = vals.filter((v): v is number => v !== null && v !== undefined);
      return nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : null;
    };
    return {
      count: suiteDone.length,
      direct: {
        tokens: avg(suiteDone.map((r) => r.result!.direct.usage.total_tokens)),
        cost: avg(suiteDone.map((r) => r.result!.direct.cost.total_cost_usd)),
        latency: avg(suiteDone.map((r) => r.result!.direct.latency_ms)),
      },
      smart: {
        tokens: avg(suiteDone.map((r) => r.result!.smart.usage.total_tokens)),
        cost: avg(suiteDone.map((r) => r.result!.smart.cost.total_cost_usd)),
        latency: avg(suiteDone.map((r) => r.result!.smart.latency_ms)),
      },
    };
  }, [suiteDone]);

  return (
    <DashboardLayout activeItem="benchmark">
      <Header title="Benchmark" subtitle="Direct LLM vs SmartLLM — real measurements" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        {/* Controls */}
        <AnimatedCard className="p-5 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-white/40 block">Benchmark Prompt (enter your own to reproduce)</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={2}
              className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-violet-500 font-mono resize-none"
              placeholder="e.g. Write a python script to parse a CSV..."
            />
          </div>
          <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 px-3 py-2 flex flex-wrap items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest text-indigo-300/80">Direct LLM baseline</span>
            <Badge variant="info">{baselineLabel}</Badge>
            <span className="text-[11px] text-white/35">
              OpenAI is not required — any configured provider can be the Direct baseline. SmartLLM still auto-routes.
            </span>
          </div>

          {modelsLoaded && availableProviders.length === 0 && (
            <p className="text-sm text-amber-300/80">
              No providers are configured. Set at least one key in backend/.env (for example XAI_API_KEY).
            </p>
          )}

          <div className="flex flex-col lg:flex-row gap-4 items-end">
            <div className="w-full lg:w-48 space-y-2">
              <label className="text-xs text-white/40 block">Baseline Provider (Direct LLM)</label>
              <select
                value={baselineProvider}
                onChange={(e) => setBaselineProvider(e.target.value)}
                disabled={availableProviders.length === 0}
                className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-violet-500 disabled:opacity-50"
              >
                {availableProviders.length === 0 && <option value="">No providers available</option>}
                {availableProviders.map((p) => (
                  <option key={p} value={p}>{PROVIDER_LABELS[p] ?? p}</option>
                ))}
              </select>
            </div>
            <div className="w-full lg:w-56 space-y-2">
              <label className="text-xs text-white/40 block">Baseline Model (Direct LLM)</label>
              <select
                value={baselineModel}
                onChange={(e) => setBaselineModel(e.target.value)}
                disabled={baselineModels.length === 0}
                className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-violet-500 disabled:opacity-50"
              >
                {baselineModels.map((m) => (
                  <option key={m.model} value={m.model}>{m.model}</option>
                ))}
              </select>
            </div>
            <div className="w-full lg:w-40 space-y-2">
              <label className="text-xs text-white/40 block">SmartLLM Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full bg-[#0F0F1A] border border-white/10 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-violet-500"
              >
                <option value="cost">Cost</option>
                <option value="speed">Speed</option>
                <option value="balanced">Balanced</option>
                <option value="quality">Quality</option>
              </select>
            </div>
            <label className="flex items-center gap-2 pb-2.5 cursor-pointer whitespace-nowrap">
              <input
                type="checkbox"
                checked={optimize}
                onChange={(e) => setOptimize(e.target.checked)}
                className="accent-violet-500 w-4 h-4"
              />
              <span className="text-xs text-white/60">Prompt optimization</span>
            </label>
            <button
              onClick={run}
              disabled={loading || suiteRunning || !prompt.trim() || !baselineReady}
              className="w-full lg:w-44 p-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LineChart className="w-4 h-4" />}
              {loading ? "Running..." : "Run Benchmark"}
            </button>
          </div>
        </AnimatedCard>

        {error && (
          <AnimatedCard className="p-4 border-red-500/20 bg-red-500/5">
            <p className="text-sm font-semibold text-red-400 mb-1">Benchmark failed</p>
            <p className="text-sm text-red-300/80">{error}</p>
          </AnimatedCard>
        )}

        {loading && (
          <div className="h-[200px] flex flex-col items-center justify-center border border-white/5 rounded-2xl bg-white/[0.02]">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mb-3" />
            <p className="text-white/40 text-sm">Running the same prompt through both pipelines...</p>
          </div>
        )}

        {result && (
          <>
            {/* Comparison summary */}
            <AnimatedCard className="p-5">
              <h3 className="text-sm font-semibold text-white mb-1">Measured Change (SmartLLM vs Direct)</h3>
              <p className="text-[11px] text-white/35 mb-4">{result.comparison.note}</p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: "Tokens", v: result.comparison.token_change_percent },
                  { label: "Cost", v: result.comparison.cost_change_percent },
                  { label: "Latency", v: result.comparison.latency_change_percent },
                ].map(({ label, v }) => (
                  <div key={label} className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 text-center">
                    <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">{label} change</p>
                    <p className={cn(
                      "text-2xl font-bold",
                      v === null ? "text-white/40 text-base" : v < 0 ? "text-emerald-400" : v > 0 ? "text-red-400" : "text-white/70"
                    )}>
                      {v === null ? "Not comparable" : formatPct(v)}
                    </p>
                  </div>
                ))}
              </div>
            </AnimatedCard>

            {/* Side by side */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[
                {
                  key: "direct" as const,
                  title: "Direct LLM",
                  sub: `Prompt → ${result.baseline?.label ?? `${result.direct.provider}/${result.direct.model}`}`,
                  data: result.direct,
                  highlight: false,
                },
                { key: "smart" as const, title: "SmartLLM", sub: "Analyzer → Optimizer → Router → model", data: result.smart, highlight: true },
              ].map(({ key, title, sub, data, highlight }) => (
                <AnimatedCard
                  key={key}
                  className={cn("p-6 relative overflow-hidden", highlight ? "border-violet-500/30 bg-violet-500/5" : "border-white/5")}
                >
                  <div className="absolute top-0 right-0 p-4">
                    <div className={cn(
                      "text-xs font-semibold px-2 py-1 rounded flex items-center gap-1",
                      highlight ? "text-violet-300 bg-violet-500/20" : "text-white/30 bg-white/5"
                    )}>
                      {highlight && <CheckCircle2 className="w-3 h-3" />} {title}
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-white">{title}</h3>
                  <p className="text-xs text-white/35 mb-5">{sub}</p>

                  <div className="space-y-1 mb-5 text-sm">
                    {[
                      ["Provider", data.provider],
                      ["Model", data.model],
                      ["Input tokens", String(data.usage.prompt_tokens)],
                      ["Output tokens", String(data.usage.completion_tokens)],
                      ["Total tokens", String(data.usage.total_tokens)],
                      ["Latency", `${Math.round(data.latency_ms)} ms`],
                      ["Cost", formatCost(data.cost.total_cost_usd, data.cost.pricing_available)],
                    ].map(([label, value]) => (
                      <div key={label} className="flex justify-between items-center py-1.5 border-b border-white/5">
                        <span className="text-white/40">{label}</span>
                        <span className="font-mono text-white/85">{value}</span>
                      </div>
                    ))}
                  </div>

                  <div>
                    <h4 className="text-xs text-white/40 mb-2">Response Output</h4>
                    <div className="bg-black/40 border border-white/5 rounded p-3 h-[220px] overflow-y-auto text-xs font-mono text-white/75 whitespace-pre-wrap">
                      {data.content}
                    </div>
                  </div>
                </AnimatedCard>
              ))}
            </div>

            {/* Why this model */}
            <AnimatedCard className="p-5 border-violet-500/20 bg-violet-500/5">
              <div className="flex items-center gap-2 mb-2">
                <Route className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-semibold text-white">Why SmartLLM selected this model</h3>
              </div>
              <p className="text-sm text-white/65 leading-relaxed">{result.smart.routing.reason}</p>
              {result.smart.optimization?.optimization_applied && (
                <p className="text-xs text-emerald-300/70 mt-2">
                  Prompt optimization removed an estimated {result.smart.optimization.reduction_percent}% of prompt tokens
                  ({result.smart.optimization.techniques_applied.join(", ")}).
                </p>
              )}
            </AnimatedCard>

            {/* How is this calculated */}
            <AnimatedCard className="p-5">
              <button
                onClick={() => setShowFormulas(!showFormulas)}
                className="flex items-center gap-2 text-sm font-semibold text-white/80 hover:text-white transition-colors"
              >
                <HelpCircle className="w-4 h-4 text-blue-400" />
                How is this calculated?
                <span className="text-white/30 text-xs">{showFormulas ? "(hide)" : "(show)"}</span>
              </button>
              {showFormulas && (
                <div className="mt-4 space-y-2">
                  {Object.entries(result.formulas).map(([key, formula]) => (
                    <div key={key} className="bg-white/[0.03] border border-white/[0.06] rounded-lg p-3">
                      <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">{key}</p>
                      <p className="text-xs text-white/65 font-mono">{formula}</p>
                    </div>
                  ))}
                </div>
              )}
            </AnimatedCard>
          </>
        )}

        {/* Benchmark suite */}
        <AnimatedCard className="p-5">
          <div className="flex items-center justify-between gap-4 flex-wrap mb-4">
            <div>
              <div className="flex items-center gap-2">
                <ListChecks className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-semibold text-white">Benchmark Suite</h3>
              </div>
              <p className="text-xs text-white/35 mt-1">
                Runs {SUITE_PROMPTS.length} standard prompts (coding, explanation, summarization, SQL, reasoning,
                short and long responses) through both pipelines. Results appear only after real requests execute.
              </p>
            </div>
            <button
              onClick={runSuite}
              disabled={suiteRunning || loading || !baselineReady}
              className="px-4 py-2 bg-amber-600/80 hover:bg-amber-500/80 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              {suiteRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <ListChecks className="w-4 h-4" />}
              {suiteRunning ? `Running ${suiteDone.length + 1}/${SUITE_PROMPTS.length}...` : "Run Suite"}
            </button>
          </div>

          {suiteAgg && (
            <div className="mb-4 bg-white/[0.02] border border-white/[0.06] rounded-xl p-4">
              <p className="text-[10px] text-white/35 uppercase tracking-widest mb-3">
                Aggregate averages over {suiteAgg.count} completed run(s)
              </p>
              <div className="grid grid-cols-3 text-[10px] text-white/35 uppercase tracking-widest pb-2 border-b border-white/10">
                <span>Metric</span>
                <span className="text-right pr-6">Direct LLM</span>
                <span className="text-right">SmartLLM</span>
              </div>
              <MetricRow label="Avg tokens" direct={suiteAgg.direct.tokens} smart={suiteAgg.smart.tokens} format={(v) => v.toFixed(0)} />
              <MetricRow label="Avg cost" direct={suiteAgg.direct.cost} smart={suiteAgg.smart.cost} format={(v) => `$${v.toFixed(6)}`} />
              <MetricRow label="Avg latency" direct={suiteAgg.direct.latency} smart={suiteAgg.smart.latency} format={(v) => `${Math.round(v)} ms`} />
            </div>
          )}

          <div className="space-y-1">
            {suite.map((row, i) => (
              <div key={i} className="flex items-center gap-3 py-2 border-b border-white/5 last:border-0 text-sm">
                <Badge variant="neutral" className="w-28 justify-center shrink-0">{row.category}</Badge>
                <span className="flex-1 text-white/55 truncate text-xs">{row.prompt}</span>
                {row.status === "pending" && <span className="text-[10px] text-white/25">pending</span>}
                {row.status === "running" && <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
                {row.status === "error" && (
                  <span className="text-[10px] text-red-400 max-w-[240px] truncate" title={row.error}>{row.error}</span>
                )}
                {row.status === "done" && row.result && (
                  <span className="text-[10px] font-mono text-white/50 whitespace-nowrap">
                    tok {formatPct(row.result.comparison.token_change_percent)} ·
                    cost {formatPct(row.result.comparison.cost_change_percent)} ·
                    lat {formatPct(row.result.comparison.latency_change_percent)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </AnimatedCard>
      </main>
    </DashboardLayout>
  );
}

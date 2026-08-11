"use client";

import React, { useCallback, useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar,
} from "recharts";
import { BarChart3, Loader2, Database, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, ApiError, AnalyticsOverview } from "@/lib/api";

type Range = "today" | "7d" | "30d" | "all";

const RANGES: { id: Range; label: string }[] = [
  { id: "today", label: "Today" },
  { id: "7d", label: "Last 7 days" },
  { id: "30d", label: "Last 30 days" },
  { id: "all", label: "All time" },
];

const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0D0D1A]/95 border border-white/[0.10] rounded-xl px-3 py-2.5 shadow-2xl">
      <p className="text-[10px] text-white/40 mb-1">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 text-xs">
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-white/50 capitalize">{entry.name}:</span>
          <span className="text-white font-medium">{Number(entry.value).toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

function StatCard({ label, value, sub }: { label: string; value: React.ReactNode; sub?: string }) {
  return (
    <AnimatedCard padding="sm">
      <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">{label}</p>
      <p className="text-xl font-bold text-white">{value}</p>
      {sub && <p className="text-[10px] text-white/30 mt-0.5">{sub}</p>}
    </AnimatedCard>
  );
}

function SeriesChart({ title, dataKey, color, data }: {
  title: string; dataKey: string; color: string;
  data: NonNullable<AnalyticsOverview["time_series"]>;
}) {
  return (
    <AnimatedCard padding="sm">
      <p className="text-xs font-semibold text-white/70 mb-3">{title}</p>
      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.2} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} />
            <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={1.5} fill={`url(#grad-${dataKey})`} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </AnimatedCard>
  );
}

export default function AnalyticsPage() {
  const [range, setRange] = useState<Range>("all");
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (r: Range) => {
    setLoading(true);
    setError(null);
    try {
      setData(await api.analytics(r));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load analytics.");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(range);
  }, [range, load]);

  const totals = data?.totals;

  return (
    <DashboardLayout activeItem="analytics">
      <Header title="Analytics" subtitle="Real stored request data" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        {/* Range filter */}
        <div className="flex items-center gap-1 p-1 bg-white/[0.04] rounded-xl border border-white/[0.06] w-fit">
          {RANGES.map((r) => (
            <button
              key={r.id}
              onClick={() => setRange(r.id)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                range === r.id ? "bg-white/10 text-white" : "text-white/35 hover:text-white/60"
              )}
            >
              {r.label}
            </button>
          ))}
        </div>

        {loading && (
          <div className="h-[300px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
          </div>
        )}

        {error && !loading && (
          <AnimatedCard className="p-6 border-red-500/20 bg-red-500/5 text-center">
            <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-red-400 mb-1">Could not load analytics</p>
            <p className="text-sm text-red-300/70">{error}</p>
          </AnimatedCard>
        )}

        {!loading && !error && data && !data.has_data && (
          <AnimatedCard className="p-12 text-center">
            <Database className="w-10 h-10 text-white/15 mx-auto mb-4" />
            <p className="text-base font-semibold text-white/60 mb-1">No request data yet</p>
            <p className="text-sm text-white/35 max-w-md mx-auto">
              {data.database_available
                ? "Run some requests in the Playground or Benchmark and real usage analytics will appear here. No fake statistics are shown."
                : "The database is unavailable, so stored analytics cannot be read right now."}
            </p>
          </AnimatedCard>
        )}

        {!loading && !error && data?.has_data && totals && (
          <>
            <section className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
              <StatCard label="Total Requests" value={totals.requests.toLocaleString()} />
              <StatCard label="Total Tokens" value={totals.total_tokens.toLocaleString()} sub={`${totals.input_tokens.toLocaleString()} in / ${totals.output_tokens.toLocaleString()} out`} />
              <StatCard label="Total Est. Cost" value={`$${totals.total_cost_usd.toFixed(6)}`} />
              <StatCard label="Avg Latency" value={`${Math.round(totals.avg_latency_ms)} ms`} />
              <StatCard label="Avg Tokens/Req" value={totals.avg_tokens_per_request.toLocaleString()} />
              <StatCard
                label="Optimized Requests"
                value={data.optimization?.optimized_requests ?? 0}
                sub={data.optimization && data.optimization.optimized_requests > 0
                  ? `avg est. reduction ${data.optimization.avg_estimated_reduction_percent}%`
                  : undefined}
              />
            </section>

            {data.time_series && data.time_series.length > 0 && (
              <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <SeriesChart title="Cost over time (USD)" dataKey="cost_usd" color="#F59E0B" data={data.time_series} />
                <SeriesChart title="Token usage over time" dataKey="tokens" color="#3B82F6" data={data.time_series} />
                <SeriesChart title="Avg latency over time (ms)" dataKey="avg_latency_ms" color="#10B981" data={data.time_series} />
              </section>
            )}

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <AnimatedCard padding="sm">
                <p className="text-xs font-semibold text-white/70 mb-3">Provider usage (requests)</p>
                <div className="h-52">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.provider_usage} margin={{ top: 5, right: 10, left: -15, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                      <XAxis dataKey="provider" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.35)" }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }} tickLine={false} axisLine={false} allowDecimals={false} />
                      <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                      <Bar dataKey="requests" fill="#8B5CF6" radius={[3, 3, 0, 0]} opacity={0.85} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </AnimatedCard>

              <AnimatedCard padding="sm">
                <p className="text-xs font-semibold text-white/70 mb-3">Model usage</p>
                <div className="space-y-2 max-h-52 overflow-y-auto">
                  {data.model_usage?.map((m) => (
                    <div key={`${m.provider}-${m.model}`} className="flex items-center justify-between gap-3 py-1.5 border-b border-white/5 last:border-0">
                      <div className="min-w-0">
                        <p className="text-xs font-mono text-white/80 truncate">{m.model}</p>
                        <p className="text-[10px] text-white/30">{m.provider}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-xs text-white/70">{m.requests} req · {m.tokens.toLocaleString()} tok</p>
                        <p className="text-[10px] text-white/35">${m.cost_usd.toFixed(6)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </AnimatedCard>
            </section>
          </>
        )}

        {!loading && !error && !data && (
          <AnimatedCard className="p-12 text-center">
            <BarChart3 className="w-10 h-10 text-white/15 mx-auto mb-4" />
            <p className="text-sm text-white/35">No analytics available.</p>
          </AnimatedCard>
        )}
      </main>
    </DashboardLayout>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Shield, Cpu, Terminal, LineChart as LineChartIcon } from "lucide-react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { MetricsGrid } from "@/components/metrics-grid";
import { WorkflowsList } from "@/components/workflows-list";
import { ActivityFeed } from "@/components/activity-feed";
import { UsageQuotaCard } from "@/components/usage-quota";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { mockWorkflows, mockActivity, mockUsageQuotas } from "@/lib/mock-data";
import { MetricCard as MetricCardType } from "@/lib/types";
import { api, AnalyticsOverview, ProviderStatus } from "@/lib/api";

function SystemStatus({ providers }: { providers: ProviderStatus[] | null }) {
  const available = providers?.filter((p) => p.available).length ?? 0;
  const total = providers?.length ?? 0;
  const allGood = providers !== null && available > 0;

  return (
    <AnimatedCard delay={0.05} padding="sm" className="border-emerald-500/10">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`w-2 h-2 rounded-full ${allGood ? "bg-emerald-400" : "bg-amber-400"}`}
          />
          <span className={`text-xs font-semibold ${allGood ? "text-emerald-400" : "text-amber-400"}`}>
            {providers === null
              ? "Checking provider status..."
              : `${available}/${total} providers available`}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {providers?.map((p) => (
            <div key={p.name} className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${p.available ? "bg-emerald-400" : "bg-white/20"}`} />
              <span className="text-[10px] text-white/35 capitalize">{p.name}</span>
            </div>
          ))}
        </div>
      </div>
    </AnimatedCard>
  );
}

function WelcomeBanner({ totalRequests }: { totalRequests: number | null }) {
  const [greeting, setGreeting] = useState("Welcome");
  useEffect(() => {
    const hour = new Date().getHours();
    setGreeting(hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening");
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-gradient-to-br from-violet-600/10 via-indigo-600/5 to-transparent p-6"
    >
      <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full bg-violet-600/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-10 -left-10 w-40 h-40 rounded-full bg-indigo-600/8 blur-3xl pointer-events-none" />

      <div className="relative flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span className="text-xs text-violet-400 font-semibold">SmartLLM Cloud</span>
            <Badge variant="default" dot>Live</Badge>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">{greeting} 👋</h2>
          <p className="text-sm text-white/40 mt-1">
            {totalRequests !== null && totalRequests > 0 ? (
              <>SmartLLM has processed <span className="text-white/70 font-medium">{totalRequests.toLocaleString()} optimized request{totalRequests === 1 ? "" : "s"}</span> so far. Open Analytics for the full picture.</>
            ) : (
              <>LLM optimization middleware: analyze → optimize → route → measure. Run your first request in the Playground.</>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <Link href="/playground" className="flex items-center gap-2 bg-white/[0.04] border border-white/[0.06] rounded-xl px-3 py-2 hover:bg-white/[0.08] transition-colors">
            <Terminal className="w-3.5 h-3.5 text-violet-400" />
            <div>
              <p className="text-[10px] text-white/30">Try it</p>
              <p className="text-xs font-semibold text-white">Playground</p>
            </div>
          </Link>
          <Link href="/benchmark" className="flex items-center gap-2 bg-white/[0.04] border border-white/[0.06] rounded-xl px-3 py-2 hover:bg-white/[0.08] transition-colors">
            <LineChartIcon className="w-3.5 h-3.5 text-emerald-400" />
            <div>
              <p className="text-[10px] text-white/30">Prove it</p>
              <p className="text-xs font-semibold text-white">Benchmark</p>
            </div>
          </Link>
        </div>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [providers, setProviders] = useState<ProviderStatus[] | null>(null);

  useEffect(() => {
    api.analytics("all").then(setAnalytics).catch(() => setAnalytics(null));
    api.providers().then(setProviders).catch(() => setProviders(null));
  }, []);

  const totals = analytics?.has_data ? analytics.totals : undefined;

  const metrics: Array<MetricCardType & { color: "violet" | "blue" | "emerald" | "amber" | "red" }> = [
    {
      label: "Requests",
      value: totals ? totals.requests : "—",
      change: 0,
      trend: "neutral",
      unit: totals ? "total" : "no data yet",
      color: "violet",
    },
    {
      label: "Tokens Used",
      value: totals ? totals.total_tokens : "—",
      change: 0,
      trend: "neutral",
      unit: totals ? "tokens" : "no data yet",
      color: "blue",
    },
    {
      label: "Avg Latency",
      value: totals ? Math.round(totals.avg_latency_ms) : "—",
      change: 0,
      trend: "neutral",
      unit: totals ? "ms" : "no data yet",
      color: "emerald",
    },
    {
      label: "Total Est. Cost",
      value: totals ? `$${totals.total_cost_usd.toFixed(4)}` : "—",
      change: 0,
      trend: "neutral",
      unit: totals ? "USD" : "no data yet",
      color: "amber",
    },
  ];

  return (
    <DashboardLayout activeItem="overview">
      <Header title="Overview" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        <WelcomeBanner totalRequests={totals ? totals.requests : null} />

        <SystemStatus providers={providers} />

        {/* Real usage metrics (from stored requests) */}
        <section>
          <MetricsGrid metrics={metrics} />
          {!totals && (
            <p className="text-[11px] text-white/25 mt-2">
              Metrics come from real recorded requests — run the Playground or Benchmark to populate them.
            </p>
          )}
        </section>

        {/* Demo panels from the original template */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <WorkflowsList workflows={mockWorkflows} delay={0.2} />
          <ActivityFeed events={mockActivity} delay={0.25} />
          <UsageQuotaCard quotas={mockUsageQuotas} delay={0.3} />
        </section>
      </main>
    </DashboardLayout>
  );
}

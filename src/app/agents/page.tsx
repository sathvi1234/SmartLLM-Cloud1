"use client";

import React from "react";
import Link from "next/link";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Bot, Terminal, LineChart } from "lucide-react";

export default function AgentsPage() {
  return (
    <DashboardLayout activeItem="agents">
      <Header title="Agents" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        <AnimatedCard className="p-12 text-center">
          <Bot className="w-12 h-12 text-white/15 mx-auto mb-4" />
          <p className="text-base font-semibold text-white/60 mb-1">No agent runtime configured</p>
          <p className="text-sm text-white/35 max-w-lg mx-auto mb-6">
            SmartLLM Cloud currently focuses on request optimization: analysis, prompt optimization, model routing,
            cost tracking and benchmarking. A persistent agent runtime is not part of this deployment, so there are
            no agents to show — this page will populate when agents are added.
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link
              href="/playground"
              className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Terminal className="w-4 h-4" /> Try the Playground
            </Link>
            <Link
              href="/benchmark"
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.06] hover:bg-white/[0.1] border border-white/10 text-white/80 rounded-lg text-sm font-medium transition-colors"
            >
              <LineChart className="w-4 h-4" /> Run a Benchmark
            </Link>
          </div>
        </AnimatedCard>
      </main>
    </DashboardLayout>
  );
}

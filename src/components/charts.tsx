"use client";

import React, { useState } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
} from "recharts";
import { motion } from "framer-motion";
import { TrendingUp, Zap, AlertTriangle, Activity } from "lucide-react";
import { AnimatedCard, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChartDataPoint } from "@/lib/types";
import { cn } from "@/lib/utils";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0D0D1A]/95 border border-white/[0.10] rounded-xl px-3 py-2.5 shadow-2xl backdrop-blur-xl">
      <p className="text-[10px] text-white/40 mb-2">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 text-xs">
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-white/50 capitalize">{entry.name}:</span>
          <span className="text-white font-medium">{entry.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

type ChartTab = "requests" | "tokens" | "latency" | "errors";

interface ChartTabConfig {
  id: ChartTab;
  label: string;
  icon: React.ReactNode;
  color: string;
  gradient: [string, string];
}

const tabs: ChartTabConfig[] = [
  { id: "requests", label: "Requests", icon: <Activity className="w-3.5 h-3.5" />, color: "#8B5CF6", gradient: ["#8B5CF620", "#8B5CF600"] },
  { id: "tokens", label: "Tokens", icon: <Zap className="w-3.5 h-3.5" />, color: "#3B82F6", gradient: ["#3B82F620", "#3B82F600"] },
  { id: "latency", label: "Latency", icon: <TrendingUp className="w-3.5 h-3.5" />, color: "#10B981", gradient: ["#10B98120", "#10B98100"] },
  { id: "errors", label: "Errors", icon: <AlertTriangle className="w-3.5 h-3.5" />, color: "#F59E0B", gradient: ["#F59E0B20", "#F59E0B00"] },
];

interface RequestsChartProps {
  data: ChartDataPoint[];
  delay?: number;
}

export function RequestsChart({ data, delay = 0 }: RequestsChartProps) {
  const [activeTab, setActiveTab] = useState<ChartTab>("requests");

  const tab = tabs.find((t) => t.id === activeTab)!;

  return (
    <AnimatedCard delay={delay} padding="none" className="col-span-2">
      <div className="p-6 pb-0">
        <CardHeader>
          <div>
            <CardTitle>Platform Telemetry</CardTitle>
            <CardDescription>24-hour rolling window · Auto-refreshing</CardDescription>
          </div>
          <div className="flex items-center gap-1 p-1 bg-white/[0.04] rounded-xl border border-white/[0.06]">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={cn(
                  "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-200",
                  activeTab === t.id
                    ? "bg-white/10 text-white shadow-sm"
                    : "text-white/35 hover:text-white/60"
                )}
              >
                {t.icon}
                <span className="hidden sm:inline">{t.label}</span>
              </button>
            ))}
          </div>
        </CardHeader>
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="h-56 px-2 pb-4"
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={`gradient-${activeTab}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={tab.gradient[0]} stopOpacity={1} />
                <stop offset="95%" stopColor={tab.gradient[1]} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }}
              tickLine={false}
              axisLine={false}
              interval={3}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: "rgba(255,255,255,0.06)", strokeWidth: 1 }} />
            <Area
              type="monotone"
              dataKey={activeTab}
              stroke={tab.color}
              strokeWidth={1.5}
              fill={`url(#gradient-${activeTab})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>
    </AnimatedCard>
  );
}

interface DistributionChartProps {
  data: ChartDataPoint[];
  delay?: number;
}

export function DistributionChart({ data, delay = 0 }: DistributionChartProps) {
  const slicedData = data.slice(-12);

  return (
    <AnimatedCard delay={delay} padding="none">
      <div className="p-6 pb-0">
        <CardHeader>
          <div>
            <CardTitle>Error Distribution</CardTitle>
            <CardDescription>Last 12 hours</CardDescription>
          </div>
        </CardHeader>
      </div>
      <div className="h-56 px-2 pb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={slicedData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }}
              tickLine={false}
              axisLine={false}
              interval={2}
            />
            <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.25)" }} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="errors" fill="#F59E0B" radius={[3, 3, 0, 0]} opacity={0.8} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </AnimatedCard>
  );
}

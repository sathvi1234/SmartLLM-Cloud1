"use client";

import React from "react";
import { motion, Variants } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn, formatNumber } from "@/lib/utils";
import { AnimatedCard } from "@/components/ui/card";
import { MetricCard as MetricCardType } from "@/lib/types";

const sparklineVariants: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: { pathLength: 1, opacity: 1, transition: { duration: 1.2, ease: "easeInOut" } },
};

function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 80;
  const h = 28;
  const pts = data.map((v, i) => ({
    x: (i / (data.length - 1)) * w,
    y: h - ((v - min) / range) * h,
  }));
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const area = `${path} L ${pts[pts.length - 1].x} ${h} L 0 ${h} Z`;

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      <defs>
        <linearGradient id={`grad-${color}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#grad-${color})`} />
      <motion.path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        variants={sparklineVariants}
        initial="hidden"
        animate="visible"
      />
    </svg>
  );
}

const colorMap: Record<string, { text: string; glow: string; sparkline: string }> = {
  violet: { text: "text-violet-400", glow: "shadow-violet-500/10", sparkline: "#8B5CF6" },
  blue: { text: "text-blue-400", glow: "shadow-blue-500/10", sparkline: "#3B82F6" },
  emerald: { text: "text-emerald-400", glow: "shadow-emerald-500/10", sparkline: "#10B981" },
  amber: { text: "text-amber-400", glow: "shadow-amber-500/10", sparkline: "#F59E0B" },
  red: { text: "text-red-400", glow: "shadow-red-500/10", sparkline: "#EF4444" },
};

interface MetricCardProps {
  metric: MetricCardType;
  color?: "violet" | "blue" | "emerald" | "amber" | "red";
  delay?: number;
}

export function MetricCard({ metric, color = "violet", delay = 0 }: MetricCardProps) {
  const colors = colorMap[color];
  const isPositive = metric.trend === "up";
  const isNegative = metric.trend === "down";
  const isNeutral = metric.trend === "neutral";

  const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
  const trendColor = isPositive
    ? "text-emerald-400"
    : isNegative
    ? "text-red-400"
    : "text-white/30";

  return (
    <AnimatedCard
      delay={delay}
      hover
      glow
      className={cn("relative overflow-hidden group hover:shadow-xl", `hover:${colors.glow}`)}
    >
      {/* Background glow orb */}
      <div className={cn("absolute -top-6 -right-6 w-24 h-24 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500", {
        "bg-violet-500/10": color === "violet",
        "bg-blue-500/10": color === "blue",
        "bg-emerald-500/10": color === "emerald",
        "bg-amber-500/10": color === "amber",
        "bg-red-500/10": color === "red",
      })} />

      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-white/40 uppercase tracking-widest">{metric.label}</p>
          <div className="flex items-baseline gap-1.5">
            <motion.span
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: delay + 0.1 }}
              className="text-2xl font-bold text-white tracking-tight"
            >
              {typeof metric.value === "number" ? formatNumber(metric.value) : metric.value}
            </motion.span>
            {metric.unit && <span className="text-xs text-white/30 font-medium">{metric.unit}</span>}
          </div>
          <div className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}>
            <TrendIcon className="w-3 h-3" />
            <span>
              {isNeutral ? "—" : `${isPositive ? "+" : ""}${metric.change}%`}
            </span>
            <span className="text-white/20 font-normal">vs last period</span>
          </div>
        </div>
        <div className="opacity-80">
          {metric.sparkline && (
            <Sparkline data={metric.sparkline} color={colors.sparkline} />
          )}
        </div>
      </div>
    </AnimatedCard>
  );
}

interface MetricsGridProps {
  metrics: Array<MetricCardType & { color?: "violet" | "blue" | "emerald" | "amber" | "red" }>;
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {metrics.map((metric, i) => (
        <MetricCard key={metric.label} metric={metric} color={metric.color ?? "violet"} delay={i * 0.08} />
      ))}
    </div>
  );
}

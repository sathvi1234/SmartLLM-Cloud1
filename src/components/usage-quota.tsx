"use client";

import React from "react";
import { motion } from "framer-motion";
import { Zap, HardDrive, GitBranch, BarChart3, AlertTriangle } from "lucide-react";
import { AnimatedCard, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { UsageQuota } from "@/lib/types";
import { cn, formatNumber } from "@/lib/utils";

const iconMap: Record<string, React.ReactNode> = {
  violet: <Zap className="w-3.5 h-3.5 text-violet-400" />,
  blue: <BarChart3 className="w-3.5 h-3.5 text-blue-400" />,
  emerald: <HardDrive className="w-3.5 h-3.5 text-emerald-400" />,
  amber: <GitBranch className="w-3.5 h-3.5 text-amber-400" />,
};

interface UsageQuotaCardProps {
  quotas: UsageQuota[];
  delay?: number;
}

export function UsageQuotaCard({ quotas, delay = 0 }: UsageQuotaCardProps) {
  return (
    <AnimatedCard delay={delay}>
      <CardHeader>
        <div>
          <CardTitle>Usage & Quotas</CardTitle>
          <CardDescription>Current billing period</CardDescription>
        </div>
        <span className="text-[10px] text-white/25 bg-white/[0.04] border border-white/[0.06] rounded-lg px-2 py-1">
          Resets in 18d
        </span>
      </CardHeader>

      <div className="space-y-5">
        {quotas.map((quota, i) => {
          const pct = (quota.used / quota.total) * 100;
          const isWarning = pct > 75;
          const isCritical = pct > 90;
          const effectiveColor = isCritical ? "red" : isWarning ? "amber" : quota.color as any;

          return (
            <motion.div
              key={quota.label}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: delay + i * 0.08 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {iconMap[quota.color]}
                  <span className="text-xs font-medium text-white/70">{quota.label}</span>
                  {isCritical && (
                    <AlertTriangle className="w-3 h-3 text-red-400 animate-pulse" />
                  )}
                </div>
                <div className="text-right">
                  <span className={cn("text-xs font-semibold", isCritical ? "text-red-400" : isWarning ? "text-amber-400" : "text-white/70")}>
                    {pct.toFixed(0)}%
                  </span>
                </div>
              </div>
              <Progress value={quota.used} max={quota.total} color={effectiveColor} size="md" />
              <div className="flex items-center justify-between text-[10px] text-white/25">
                <span>
                  {quota.used >= 1_000_000
                    ? `${(quota.used / 1_000_000).toFixed(1)}M`
                    : quota.used >= 1_000
                    ? `${(quota.used / 1_000).toFixed(0)}K`
                    : quota.used} {quota.unit}
                </span>
                <span>
                  of {quota.total >= 1_000_000
                    ? `${(quota.total / 1_000_000).toFixed(0)}M`
                    : quota.total} {quota.unit}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-5 pt-4 border-t border-white/[0.05]">
        <div className="flex items-center justify-between text-xs">
          <span className="text-white/30">Monthly spend</span>
          <span className="text-white font-semibold">$246.15</span>
        </div>
        <div className="flex items-center justify-between text-xs mt-1">
          <span className="text-white/30">Projected</span>
          <span className="text-amber-400 font-medium">~$312.00</span>
        </div>
      </div>
    </AnimatedCard>
  );
}

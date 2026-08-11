"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Zap, Bot, GitBranch, AlertTriangle, Activity, Upload,
  Bell, ChevronRight
} from "lucide-react";
import { AnimatedCard, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ActivityEvent } from "@/lib/types";
import { cn } from "@/lib/utils";
import { RelativeTime } from "@/components/ui/relative-time";
import { Button } from "@/components/ui/button";

const eventConfig = {
  agent_call: { icon: Bot, color: "text-violet-400", bg: "bg-violet-500/10" },
  workflow: { icon: GitBranch, color: "text-blue-400", bg: "bg-blue-500/10" },
  error: { icon: AlertTriangle, color: "text-red-400", bg: "bg-red-500/10" },
  deploy: { icon: Upload, color: "text-emerald-400", bg: "bg-emerald-500/10" },
  token: { icon: Zap, color: "text-amber-400", bg: "bg-amber-500/10" },
  alert: { icon: Bell, color: "text-rose-400", bg: "bg-rose-500/10" },
};

const severityColors = {
  success: "border-l-emerald-500/60",
  warning: "border-l-amber-500/60",
  error: "border-l-red-500/60",
  info: "border-l-blue-500/60",
};

interface ActivityFeedProps {
  events: ActivityEvent[];
  delay?: number;
}

export function ActivityFeed({ events, delay = 0 }: ActivityFeedProps) {
  return (
    <AnimatedCard delay={delay}>
      <CardHeader>
        <div>
          <CardTitle>Activity Feed</CardTitle>
          <CardDescription>Real-time event stream</CardDescription>
        </div>
        <div className="flex items-center gap-1.5">
          <motion.div
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1.5 h-1.5 rounded-full bg-emerald-400"
          />
          <span className="text-[10px] text-emerald-400 font-medium">Live</span>
        </div>
      </CardHeader>

      <div className="space-y-0">
        {events.map((event, i) => {
          const cfg = eventConfig[event.type];
          const Icon = cfg.icon;
          const borderColor = severityColors[event.severity];

          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.06 }}
              className={cn(
                "flex items-start gap-3 py-3 border-b border-white/[0.04] last:border-0",
                "-mx-6 px-6 pl-5 border-l-2 transition-colors hover:bg-white/[0.01] cursor-default",
                borderColor
              )}
            >
              <div className={cn("w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5", cfg.bg)}>
                <Icon className={cn("w-3.5 h-3.5", cfg.color)} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white/70 leading-relaxed">{event.message}</p>
                <p className="text-[10px] text-white/25 mt-0.5">
                  <RelativeTime date={event.timestamp} />
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {events.length === 0 && (
        <div className="py-12 text-center">
          <Activity className="w-8 h-8 text-white/15 mx-auto mb-3" />
          <p className="text-sm text-white/30 font-medium">No recent activity</p>
          <p className="text-xs text-white/15 mt-1">Events will appear here in real-time</p>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-white/[0.05]">
        <Button variant="ghost" size="sm" className="w-full" rightIcon={<ChevronRight className="w-3.5 h-3.5" />}>
          View all events
        </Button>
      </div>
    </AnimatedCard>
  );
}

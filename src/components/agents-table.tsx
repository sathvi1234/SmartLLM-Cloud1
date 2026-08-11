"use client";

import React from "react";
import { motion } from "framer-motion";
import { Bot, AlertCircle, Clock, Zap, MoreHorizontal, ChevronRight } from "lucide-react";
import { AnimatedCard, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Agent } from "@/lib/types";
import { cn, formatNumber } from "@/lib/utils";

const statusConfig = {
  active: { label: "Active", variant: "success" as const, dot: true },
  idle: { label: "Idle", variant: "neutral" as const, dot: false },
  error: { label: "Error", variant: "error" as const, dot: true },
  training: { label: "Training", variant: "warning" as const, dot: true },
};

const modelColors: Record<string, string> = {
  "gpt-4o": "text-violet-400",
  "claude-3-5-sonnet": "text-amber-400",
  "text-embedding-3-large": "text-blue-400",
  "gpt-4o-vision": "text-rose-400",
  "gemini-1.5-pro": "text-emerald-400",
};

interface AgentRowProps {
  agent: Agent;
  index: number;
}

function AgentRow({ agent, index }: AgentRowProps) {
  const status = statusConfig[agent.status];
  const modelColor = modelColors[agent.model] ?? "text-white/50";
  const successPct = agent.successRate;
  const isError = agent.status === "error";

  return (
    <motion.tr
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="group border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
    >
      <td className="py-3.5 pr-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-8 h-8 rounded-xl flex items-center justify-center shrink-0 transition-colors",
            isError ? "bg-red-500/10" : "bg-white/[0.05] group-hover:bg-white/[0.08]"
          )}>
            <Bot className={cn("w-4 h-4", isError ? "text-red-400" : "text-white/40")} />
          </div>
          <div>
            <p className="text-sm font-medium text-white/90">{agent.name}</p>
            <p className={cn("text-xs font-mono", modelColor)}>{agent.model}</p>
          </div>
        </div>
      </td>
      <td className="py-3.5 pr-4">
        <Badge variant={status.variant} dot={status.dot}>{status.label}</Badge>
      </td>
      <td className="py-3.5 pr-4 hidden md:table-cell">
        <div className="flex items-center gap-1.5 text-xs text-white/50">
          <Zap className="w-3 h-3 text-violet-400" />
          {formatNumber(agent.requests)}
        </div>
      </td>
      <td className="py-3.5 pr-4 hidden lg:table-cell">
        <div className="flex items-center gap-1.5 text-xs text-white/50">
          <Clock className="w-3 h-3 text-blue-400" />
          {agent.latency}ms
        </div>
      </td>
      <td className="py-3.5 pr-4 hidden lg:table-cell">
        <div className="flex items-center gap-2">
          <div className="flex-1 max-w-[60px] h-1 bg-white/[0.06] rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full",
                successPct > 95 ? "bg-emerald-500" : successPct > 80 ? "bg-amber-500" : "bg-red-500"
              )}
              style={{ width: `${successPct}%` }}
            />
          </div>
          <span className={cn("text-xs font-medium",
            successPct > 95 ? "text-emerald-400" : successPct > 80 ? "text-amber-400" : "text-red-400"
          )}>
            {successPct}%
          </span>
        </div>
      </td>
      <td className="py-3.5 hidden xl:table-cell">
        <div className="flex flex-wrap gap-1">
          {agent.tags.map((tag) => (
            <span key={tag} className="text-[10px] bg-white/[0.04] text-white/30 border border-white/[0.06] rounded-md px-1.5 py-0.5">
              {tag}
            </span>
          ))}
        </div>
      </td>
      <td className="py-3.5">
        <button className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-white/[0.06] text-white/30 hover:text-white/60">
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </td>
    </motion.tr>
  );
}

interface AgentsTableProps {
  agents: Agent[];
  delay?: number;
}

export function AgentsTable({ agents, delay = 0 }: AgentsTableProps) {
  return (
    <AnimatedCard delay={delay} padding="none">
      <div className="p-6 pb-0">
        <CardHeader>
          <div>
            <CardTitle>Active Agents</CardTitle>
            <CardDescription>{agents.length} agents deployed · {agents.filter(a => a.status === "active").length} online</CardDescription>
          </div>
          <Button variant="outline" size="sm" rightIcon={<ChevronRight className="w-3.5 h-3.5" />}>
            View all
          </Button>
        </CardHeader>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/[0.06]">
              {["Agent", "Status", "Requests", "Latency", "Success Rate", "Tags", ""].map((h) => (
                <th key={h} className={cn(
                  "px-0 pb-3 pl-6 first:pl-6 text-left text-[10px] font-semibold text-white/25 uppercase tracking-widest",
                  h === "Requests" && "hidden md:table-cell",
                  h === "Latency" && "hidden lg:table-cell",
                  h === "Success Rate" && "hidden lg:table-cell",
                  h === "Tags" && "hidden xl:table-cell",
                )}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {agents.map((agent, i) => (
              <AgentRow key={agent.id} agent={agent} index={i} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {agents.length === 0 && (
        <div className="py-16 text-center">
          <Bot className="w-8 h-8 text-white/15 mx-auto mb-3" />
          <p className="text-sm text-white/30 font-medium">No agents deployed</p>
          <p className="text-xs text-white/15 mt-1">Deploy your first AI agent to get started</p>
        </div>
      )}
    </AnimatedCard>
  );
}

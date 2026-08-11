"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2, XCircle, Clock, Loader2, GitBranch, ChevronRight,
} from "lucide-react";
import { AnimatedCard, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { WorkflowRun } from "@/lib/types";
import { cn } from "@/lib/utils";
import { RelativeTime } from "@/components/ui/relative-time";

const statusConfig = {
  running: {
    icon: <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />,
    badge: "info" as const,
    label: "Running",
  },
  completed: {
    icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />,
    badge: "success" as const,
    label: "Completed",
  },
  failed: {
    icon: <XCircle className="w-3.5 h-3.5 text-red-400" />,
    badge: "error" as const,
    label: "Failed",
  },
  queued: {
    icon: <Clock className="w-3.5 h-3.5 text-amber-400" />,
    badge: "warning" as const,
    label: "Queued",
  },
};

interface WorkflowItemProps {
  workflow: WorkflowRun;
  index: number;
}

function WorkflowItem({ workflow, index }: WorkflowItemProps) {
  const status = statusConfig[workflow.status];
  const pct = (workflow.completedSteps / workflow.steps) * 100;
  const progressColor = workflow.status === "failed"
    ? "red"
    : workflow.status === "completed"
    ? "emerald"
    : workflow.status === "running"
    ? "blue"
    : "amber";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.07 }}
      className="group flex items-start gap-4 py-3.5 border-b border-white/[0.05] last:border-0 hover:bg-white/[0.01] -mx-6 px-6 transition-colors cursor-pointer"
    >
      <div className="mt-0.5 w-7 h-7 rounded-lg bg-white/[0.04] flex items-center justify-center shrink-0">
        {status.icon}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="text-sm font-medium text-white/85 truncate">{workflow.name}</p>
          <Badge variant={status.badge} className="shrink-0">{status.label}</Badge>
        </div>

        <div className="flex items-center gap-3 mb-2">
          <span className="text-[10px] text-white/30 font-mono">
            {workflow.id}
          </span>
          <span className="text-[10px] text-white/20">·</span>
          <RelativeTime date={workflow.startedAt} className="text-[10px] text-white/30" />
          <span className="text-[10px] text-white/20">·</span>
          <span className="text-[10px] text-white/30">
            via {workflow.triggeredBy}
          </span>
          {workflow.duration && (
            <>
              <span className="text-[10px] text-white/20">·</span>
              <span className="text-[10px] text-white/30">{workflow.duration}s</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Progress
            value={workflow.completedSteps}
            max={workflow.steps}
            color={progressColor as any}
            size="sm"
            className="flex-1"
          />
          <span className="text-[10px] text-white/30 shrink-0">
            {workflow.completedSteps}/{workflow.steps} steps
          </span>
        </div>
      </div>

      <button className="opacity-0 group-hover:opacity-100 transition-opacity mt-1 p-1 rounded-lg hover:bg-white/[0.06] text-white/30 hover:text-white/60">
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    </motion.div>
  );
}

interface WorkflowsListProps {
  workflows: WorkflowRun[];
  delay?: number;
}

export function WorkflowsList({ workflows, delay = 0 }: WorkflowsListProps) {
  const running = workflows.filter((w) => w.status === "running").length;
  const failed = workflows.filter((w) => w.status === "failed").length;

  return (
    <AnimatedCard delay={delay}>
      <CardHeader>
        <div>
          <CardTitle>Workflow Runs</CardTitle>
          <CardDescription>
            {running > 0 && <span className="text-blue-400">{running} running</span>}
            {running > 0 && failed > 0 && <span className="text-white/20"> · </span>}
            {failed > 0 && <span className="text-red-400">{failed} failed</span>}
            {running === 0 && failed === 0 && "All workflows nominal"}
          </CardDescription>
        </div>
        <Button variant="outline" size="sm" leftIcon={<GitBranch className="w-3.5 h-3.5" />}>
          New run
        </Button>
      </CardHeader>

      <div>
        {workflows.length === 0 ? (
          <div className="py-12 text-center">
            <GitBranch className="w-8 h-8 text-white/15 mx-auto mb-3" />
            <p className="text-sm text-white/30 font-medium">No workflow runs</p>
            <p className="text-xs text-white/15 mt-1">Create your first workflow to automate tasks</p>
          </div>
        ) : (
          workflows.map((wf, i) => <WorkflowItem key={wf.id} workflow={wf} index={i} />)
        )}
      </div>
    </AnimatedCard>
  );
}

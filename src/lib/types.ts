export interface Agent {
  id: string;
  name: string;
  status: "active" | "idle" | "error" | "training";
  model: string;
  requests: number;
  latency: number;
  successRate: number;
  lastActive: Date;
  tags: string[];
  tokensUsed: number;
  cost: number;
}

export interface WorkflowRun {
  id: string;
  name: string;
  status: "running" | "completed" | "failed" | "queued";
  startedAt: Date;
  duration?: number;
  steps: number;
  completedSteps: number;
  triggeredBy: string;
}

export interface MetricCard {
  label: string;
  value: string | number;
  change: number;
  trend: "up" | "down" | "neutral";
  unit?: string;
  sparkline?: number[];
}

export interface ActivityEvent {
  id: string;
  type: "agent_call" | "workflow" | "error" | "deploy" | "token" | "alert";
  message: string;
  timestamp: Date;
  severity: "info" | "warning" | "error" | "success";
  agentId?: string;
}

export interface ChartDataPoint {
  time: string;
  requests: number;
  latency: number;
  tokens: number;
  errors: number;
}

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  href: string;
  badge?: number;
  shortcut?: string;
}

export interface UsageQuota {
  label: string;
  used: number;
  total: number;
  unit: string;
  color: string;
}

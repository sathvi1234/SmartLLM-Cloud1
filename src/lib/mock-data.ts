import { Agent, WorkflowRun, ActivityEvent, ChartDataPoint, UsageQuota } from "./types";

export const mockAgents: Agent[] = [
  {
    id: "agt-001",
    name: "GPT-4o Orchestrator",
    status: "active",
    model: "gpt-4o",
    requests: 12847,
    latency: 234,
    successRate: 99.2,
    lastActive: new Date(Date.now() - 2 * 60 * 1000),
    tags: ["production", "primary"],
    tokensUsed: 4_820_000,
    cost: 96.4,
  },
  {
    id: "agt-002",
    name: "Claude Researcher",
    status: "active",
    model: "claude-3-5-sonnet",
    requests: 8234,
    latency: 312,
    successRate: 98.7,
    lastActive: new Date(Date.now() - 5 * 60 * 1000),
    tags: ["research", "analysis"],
    tokensUsed: 3_100_000,
    cost: 62.0,
  },
  {
    id: "agt-003",
    name: "Embeddings Engine",
    status: "idle",
    model: "text-embedding-3-large",
    requests: 45920,
    latency: 45,
    successRate: 99.9,
    lastActive: new Date(Date.now() - 15 * 60 * 1000),
    tags: ["embeddings", "search"],
    tokensUsed: 12_000_000,
    cost: 24.0,
  },
  {
    id: "agt-004",
    name: "Vision Analyzer",
    status: "error",
    model: "gpt-4o-vision",
    requests: 1203,
    latency: 1820,
    successRate: 87.3,
    lastActive: new Date(Date.now() - 32 * 60 * 1000),
    tags: ["vision", "multimodal"],
    tokensUsed: 890_000,
    cost: 44.5,
  },
  {
    id: "agt-005",
    name: "Gemini Pro Agent",
    status: "training",
    model: "gemini-1.5-pro",
    requests: 3401,
    latency: 198,
    successRate: 96.1,
    lastActive: new Date(Date.now() - 48 * 60 * 1000),
    tags: ["staging", "experimental"],
    tokensUsed: 1_540_000,
    cost: 19.25,
  },
];

export const mockWorkflows: WorkflowRun[] = [
  {
    id: "wf-001",
    name: "Document Ingestion Pipeline",
    status: "running",
    startedAt: new Date(Date.now() - 4 * 60 * 1000),
    steps: 8,
    completedSteps: 5,
    triggeredBy: "API",
  },
  {
    id: "wf-002",
    name: "Daily Report Generation",
    status: "completed",
    startedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    duration: 142,
    steps: 12,
    completedSteps: 12,
    triggeredBy: "Scheduler",
  },
  {
    id: "wf-003",
    name: "Customer Onboarding AI",
    status: "queued",
    startedAt: new Date(Date.now() - 1 * 60 * 1000),
    steps: 6,
    completedSteps: 0,
    triggeredBy: "Webhook",
  },
  {
    id: "wf-004",
    name: "Content Moderation Batch",
    status: "failed",
    startedAt: new Date(Date.now() - 30 * 60 * 1000),
    duration: 89,
    steps: 4,
    completedSteps: 2,
    triggeredBy: "Manual",
  },
];

export const mockActivity: ActivityEvent[] = [
  {
    id: "evt-001",
    type: "agent_call",
    message: "GPT-4o Orchestrator processed 847 requests",
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    severity: "success",
    agentId: "agt-001",
  },
  {
    id: "evt-002",
    type: "alert",
    message: "Vision Analyzer error rate exceeded 12% threshold",
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    severity: "error",
    agentId: "agt-004",
  },
  {
    id: "evt-003",
    type: "workflow",
    message: "Daily Report Generation completed in 2m 22s",
    timestamp: new Date(Date.now() - 22 * 60 * 1000),
    severity: "success",
  },
  {
    id: "evt-004",
    type: "token",
    message: "Monthly token usage crossed 80% quota",
    timestamp: new Date(Date.now() - 35 * 60 * 1000),
    severity: "warning",
  },
  {
    id: "evt-005",
    type: "deploy",
    message: "Gemini Pro Agent v2.1 deployed to staging",
    timestamp: new Date(Date.now() - 48 * 60 * 1000),
    severity: "info",
    agentId: "agt-005",
  },
  {
    id: "evt-006",
    type: "agent_call",
    message: "Embeddings Engine processed 45.9K vectors",
    timestamp: new Date(Date.now() - 60 * 60 * 1000),
    severity: "success",
    agentId: "agt-003",
  },
];

export function generateChartData(points: number = 24): ChartDataPoint[] {
  const data: ChartDataPoint[] = [];
  const now = new Date();
  for (let i = points - 1; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hour = time.getHours();
    const base = hour >= 9 && hour <= 18 ? 1.5 : 0.6;
    data.push({
      time: time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      requests: Math.floor((Math.random() * 800 + 200) * base),
      latency: Math.floor(Math.random() * 200 + 150),
      tokens: Math.floor((Math.random() * 50000 + 10000) * base),
      errors: Math.floor(Math.random() * 15),
    });
  }
  return data;
}

export const mockUsageQuotas: UsageQuota[] = [
  { label: "API Requests", used: 847_293, total: 1_000_000, unit: "req", color: "violet" },
  { label: "Tokens", used: 22_350_000, total: 30_000_000, unit: "tok", color: "blue" },
  { label: "Storage", used: 48.3, total: 100, unit: "GB", color: "emerald" },
  { label: "Workflows", used: 82, total: 100, unit: "runs", color: "amber" },
];

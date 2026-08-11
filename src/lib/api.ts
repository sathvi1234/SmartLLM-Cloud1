/** Central API client for the SmartLLM Cloud backend. */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(
      "Backend unreachable. Start it with: uvicorn app.main:app --reload (in the backend folder).",
      0
    );
  }
  if (!res.ok) {
    let detail = `Request failed with HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Types mirroring the backend responses
// ---------------------------------------------------------------------------
export interface Usage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface CostInfo {
  input_cost_usd: number | null;
  output_cost_usd: number | null;
  total_cost_usd: number | null;
  pricing_available: boolean;
  pricing_note: string;
}

export interface OptimizationResult {
  original_prompt: string;
  optimized_prompt: string;
  estimated_tokens_before: number;
  estimated_tokens_after: number;
  reduction_percent: number;
  techniques_applied: string[];
  optimization_applied: boolean;
  note: string;
}

export interface RoutingInfo {
  selected_provider: string;
  selected_model: string;
  mode: string;
  reason: string;
  estimated_cost: number | null;
  estimated_latency_ms: number | null;
  auto_routed: boolean;
}

export interface AnalysisInfo {
  prompt_length_chars: number;
  estimated_tokens: number;
  intent: string[];
  complexity: number;
  difficulty: string;
}

export interface GenerationResult {
  content: string;
  provider: string;
  model: string;
  usage: Usage;
  latency_ms: number;
  cost: CostInfo;
  request_id: string | null;
}

export interface SmartGenerationResult extends GenerationResult {
  analysis: AnalysisInfo;
  routing: RoutingInfo;
  optimization: OptimizationResult | null;
}

export interface BenchmarkResult {
  direct: GenerationResult & {
    baseline?: { provider: string; model: string; requested_provider?: string; requested_model?: string | null };
  };
  smart: SmartGenerationResult;
  baseline?: { provider: string; model: string; label: string };
  comparison: {
    token_change_percent: number | null;
    cost_change_percent: number | null;
    latency_change_percent: number | null;
    note: string;
  };
  formulas: Record<string, string>;
}

export interface ModelInfo {
  provider: string;
  model: string;
  input_price_per_1m: number;
  output_price_per_1m: number;
  capability_score: number;
  privacy_score: number;
  context_limit: number;
  configured: boolean;
  available: boolean;
}

export interface ProviderStatus {
  name: string;
  configured: boolean;
  available: boolean;
  health_status: string;
}

export interface RequestLogItem {
  request_id: string;
  timestamp: string | null;
  provider: string;
  model: string;
  routing_mode: string;
  source: string;
  prompt_preview: string | null;
  response_preview: string | null;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  latency_ms: number;
  input_cost_usd: number | null;
  output_cost_usd: number | null;
  total_cost_usd: number | null;
  pricing_available: boolean;
  optimization_enabled: boolean;
  optimization_reduction_percent: number;
}

export interface AnalyticsOverview {
  has_data: boolean;
  database_available: boolean;
  range: string;
  totals?: {
    requests: number;
    total_tokens: number;
    input_tokens: number;
    output_tokens: number;
    total_cost_usd: number;
    avg_latency_ms: number;
    avg_tokens_per_request: number;
  };
  provider_usage?: { provider: string; requests: number; tokens: number; cost_usd: number }[];
  model_usage?: { model: string; provider: string; requests: number; tokens: number; cost_usd: number }[];
  time_series?: { date: string; requests: number; tokens: number; cost_usd: number; avg_latency_ms: number }[];
  optimization?: { optimized_requests: number; avg_estimated_reduction_percent: number };
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------
export const api = {
  smartGenerate: (body: {
    prompt: string;
    mode: string;
    provider: string;
    model_name?: string;
    optimize: boolean;
    source?: string;
  }) => request<SmartGenerationResult>("/ai/smart-generate", { method: "POST", body: JSON.stringify(body) }),

  generate: (body: { prompt: string; provider: string; model_name: string; source?: string }) =>
    request<GenerationResult>("/ai/generate", { method: "POST", body: JSON.stringify(body) }),

  benchmark: (body: {
    prompt: string;
    baseline_provider?: string;
    baseline_model?: string;
    mode: string;
    optimize: boolean;
  }) => request<BenchmarkResult>("/ai/benchmark", { method: "POST", body: JSON.stringify(body) }),

  models: () => request<{ models: ModelInfo[]; providers: Record<string, { configured: boolean; available: boolean }> }>("/ai/models"),

  providers: () => request<ProviderStatus[]>("/providers/"),

  requests: (limit = 50, offset = 0) =>
    request<{ items: RequestLogItem[]; database_available: boolean }>(`/ai/requests?limit=${limit}&offset=${offset}`),

  requestDetail: (id: string) => request<RequestLogItem>(`/ai/requests/${id}`),

  analytics: (range: "today" | "7d" | "30d" | "all") =>
    request<AnalyticsOverview>(`/analytics/overview?range=${range}`),

  /** Existing backend OAuth2 password login (username = email). */
  login: async (email: string, password: string) => {
    let res: Response;
    try {
      const body = new URLSearchParams();
      body.set("username", email);
      body.set("password", password);
      res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
    } catch {
      throw new ApiError(
        "Backend unreachable. Start it with: uvicorn app.main:app --reload (in the backend folder).",
        0
      );
    }
    if (!res.ok) {
      let detail = `Request failed with HTTP ${res.status}`;
      try {
        const data = await res.json();
        if (data?.detail) detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      } catch {
        /* non-JSON */
      }
      throw new ApiError(detail, res.status);
    }
    return res.json() as Promise<{ access_token: string; refresh_token: string; token_type: string }>;
  },

  /** Existing backend signup — used only when a registration UI calls it. */
  signup: (email: string, password: string) =>
    request<{ id: string; email: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
};

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------
export function formatCost(value: number | null | undefined, pricingAvailable = true): string {
  if (!pricingAvailable || value === null || value === undefined) return "Pricing unavailable";
  if (value === 0) return "$0.00";
  if (value < 0.0001) return `$${value.toFixed(8)}`;
  return `$${value.toFixed(6)}`;
}

export function formatPct(value: number | null | undefined): string {
  if (value === null || value === undefined) return "n/a";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
}

"use client";

import React, { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import { Header } from "@/components/header";
import { AnimatedCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { History, Loader2, AlertTriangle, ChevronDown, ChevronUp, Wand2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, ApiError, formatCost, RequestLogItem } from "@/lib/api";

function DetailField({ label, value, mono = false }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div>
      <p className="text-[10px] text-white/35 uppercase tracking-widest mb-0.5">{label}</p>
      <p className={cn("text-xs text-white/75 break-words", mono && "font-mono")}>{value}</p>
    </div>
  );
}

export default function HistoryPage() {
  const [items, setItems] = useState<RequestLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    api.requests(100)
      .then((d) => setItems(d.items))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load request history."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <DashboardLayout activeItem="history">
      <Header title="Request History" subtitle="Every completed request, stored with real measurements" />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto w-full">
        {loading && (
          <div className="h-[300px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
          </div>
        )}

        {error && !loading && (
          <AnimatedCard className="p-6 border-red-500/20 bg-red-500/5 text-center">
            <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-red-400 mb-1">Could not load request history</p>
            <p className="text-sm text-red-300/70">{error}</p>
          </AnimatedCard>
        )}

        {!loading && !error && items.length === 0 && (
          <AnimatedCard className="p-12 text-center">
            <History className="w-10 h-10 text-white/15 mx-auto mb-4" />
            <p className="text-base font-semibold text-white/60 mb-1">No requests yet</p>
            <p className="text-sm text-white/35">
              Run a prompt in the Playground or Benchmark and it will be recorded here.
            </p>
          </AnimatedCard>
        )}

        {!loading && !error && items.length > 0 && (
          <AnimatedCard padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-[10px] text-white/25 uppercase tracking-widest">
                    <th className="text-left font-semibold py-3 px-4">Date</th>
                    <th className="text-left font-semibold py-3 px-4">Provider</th>
                    <th className="text-left font-semibold py-3 px-4">Model</th>
                    <th className="text-right font-semibold py-3 px-4">Tokens</th>
                    <th className="text-right font-semibold py-3 px-4">Latency</th>
                    <th className="text-right font-semibold py-3 px-4">Cost</th>
                    <th className="text-center font-semibold py-3 px-4">Optimization</th>
                    <th className="py-3 px-4" />
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <React.Fragment key={item.request_id}>
                      <tr
                        onClick={() => setExpanded(expanded === item.request_id ? null : item.request_id)}
                        className="border-b border-white/[0.04] hover:bg-white/[0.02] cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4 text-xs text-white/60 whitespace-nowrap">
                          {item.timestamp ? new Date(item.timestamp).toLocaleString() : "—"}
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="neutral">{item.provider}</Badge>
                        </td>
                        <td className="py-3 px-4 font-mono text-xs text-white/75">{item.model}</td>
                        <td className="py-3 px-4 text-right font-mono text-white/60">{item.total_tokens}</td>
                        <td className="py-3 px-4 text-right font-mono text-white/60">{Math.round(item.latency_ms)} ms</td>
                        <td className="py-3 px-4 text-right font-mono text-white/60">
                          {formatCost(item.total_cost_usd, item.pricing_available)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {item.optimization_enabled ? (
                            <Badge variant="success">
                              <Wand2 className="w-3 h-3" /> -{item.optimization_reduction_percent}%
                            </Badge>
                          ) : (
                            <span className="text-white/25 text-xs">off</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-white/30">
                          {expanded === item.request_id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </td>
                      </tr>
                      {expanded === item.request_id && (
                        <tr className="border-b border-white/[0.04] bg-white/[0.015]">
                          <td colSpan={8} className="p-5">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                              <DetailField label="Request ID" value={item.request_id} mono />
                              <DetailField label="Routing Mode" value={item.routing_mode} />
                              <DetailField label="Source" value={item.source} />
                              <DetailField
                                label="Token Breakdown"
                                value={`${item.input_tokens} in / ${item.output_tokens} out`}
                                mono
                              />
                              <DetailField label="Input Cost" value={formatCost(item.input_cost_usd, item.pricing_available)} mono />
                              <DetailField label="Output Cost" value={formatCost(item.output_cost_usd, item.pricing_available)} mono />
                              <DetailField label="Total Cost" value={formatCost(item.total_cost_usd, item.pricing_available)} mono />
                              <DetailField
                                label="Optimization"
                                value={item.optimization_enabled
                                  ? `enabled, est. ${item.optimization_reduction_percent}% prompt reduction`
                                  : "disabled"}
                              />
                            </div>
                            {item.prompt_preview && (
                              <div className="mb-3">
                                <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">Prompt</p>
                                <div className="text-xs text-white/65 font-mono bg-black/25 rounded p-3 whitespace-pre-wrap max-h-40 overflow-y-auto">
                                  {item.prompt_preview}
                                </div>
                              </div>
                            )}
                            {item.response_preview && (
                              <div>
                                <p className="text-[10px] text-white/35 uppercase tracking-widest mb-1">Response</p>
                                <div className="text-xs text-white/65 font-mono bg-black/25 rounded p-3 whitespace-pre-wrap max-h-40 overflow-y-auto">
                                  {item.response_preview}
                                </div>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </AnimatedCard>
        )}
      </main>
    </DashboardLayout>
  );
}

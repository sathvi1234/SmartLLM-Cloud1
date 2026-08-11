"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  Gauge,
  Menu,
  Route,
  Sparkles,
  Wallet,
  X,
  Zap,
} from "lucide-react";
import { Logo } from "@/components/logo";
import { RobotVisual } from "@/components/robot-visual";
import { Button } from "@/components/ui/button";
import { isAuthenticated } from "@/lib/auth";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
];

export default function PublicOverviewPage() {
  const router = useRouter();
  const reduceMotion = useReducedMotion();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (isAuthenticated()) router.replace("/dashboard");
  }, [router]);

  return (
    <div className="relative min-h-screen text-white overflow-x-hidden">
      {/* Public page background (separate from authenticated dashboard HUD) */}
      <div className="fixed inset-0 -z-10 pointer-events-none" aria-hidden>
        <div className="absolute inset-0 bg-[#070B16]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_55%_at_70%_35%,rgba(56,189,248,0.14),transparent_55%),radial-gradient(ellipse_50%_40%_at_20%_20%,rgba(139,92,246,0.16),transparent_50%)]" />
        <div
          className="absolute inset-0 opacity-[0.18]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(56,189,248,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.10) 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
      </div>

      <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-[#070B16]/75 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          <Link href="/" className="shrink-0">
            <Logo showText />
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            {NAV.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-sm text-white/55 hover:text-white transition-colors"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-2">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Sign in
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="primary" size="sm">
                Get started
              </Button>
            </Link>
          </div>

          <button
            type="button"
            className="md:hidden p-2 rounded-lg text-white/70 hover:bg-white/[0.06]"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden border-t border-white/[0.06] px-4 py-3 space-y-2 bg-[#070B16]/95">
            {NAV.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="block py-2 text-sm text-white/70"
                onClick={() => setMobileOpen(false)}
              >
                {item.label}
              </a>
            ))}
            <div className="flex gap-2 pt-2">
              <Link href="/login" className="flex-1" onClick={() => setMobileOpen(false)}>
                <Button variant="secondary" size="sm" className="w-full">
                  Sign in
                </Button>
              </Link>
              <Link href="/login" className="flex-1" onClick={() => setMobileOpen(false)}>
                <Button variant="primary" size="sm" className="w-full">
                  Get started
                </Button>
              </Link>
            </div>
          </div>
        )}
      </header>

      <main>
        {/* Hero */}
        <section className="mx-auto max-w-6xl px-4 sm:px-6 pt-12 sm:pt-16 pb-16">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-8 items-center">
            <motion.div
              initial={reduceMotion ? false : { opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 mb-5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                <span className="text-xs font-medium text-cyan-200/90">Multi-LLM optimization middleware</span>
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-bold tracking-tight leading-[1.1]">
                Optimize every AI request
                <span className="block bg-gradient-to-r from-cyan-300 via-violet-300 to-fuchsia-300 bg-clip-text text-transparent">
                  for cost, speed, quality.
                </span>
              </h1>
              <p className="mt-5 text-base sm:text-lg text-white/50 max-w-xl leading-relaxed">
                SmartLLM Cloud intelligently analyzes, optimizes and routes your AI requests across multiple LLM providers.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="/login">
                  <Button variant="primary" size="lg" rightIcon={<ArrowRight className="w-4 h-4" />}>
                    Start free
                  </Button>
                </Link>
                <Link href="/login">
                  <Button variant="outline" size="lg">
                    See live dashboard
                  </Button>
                </Link>
              </div>
              <p className="mt-4 text-xs text-white/30">
                Analyze → Optimize → Route → Measure — with real tokens, latency, and cost.
              </p>
            </motion.div>

            <div className="relative mx-auto w-full max-w-md lg:max-w-none h-[340px] sm:h-[420px] lg:h-[480px]">
              <RobotVisual className="w-full h-full" />
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="mx-auto max-w-6xl px-4 sm:px-6 py-16 scroll-mt-20">
          <SectionHeading
            title="Built for multi-provider AI workloads"
            subtitle="Keep your product logic. SmartLLM Cloud handles analysis, safe prompt optimization, and model routing."
          />
          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Wallet, title: "Cost-aware routing", body: "Choose Cost, Speed, Balanced, or Quality modes when AUTO selects a live-usable provider." },
              { icon: Zap, title: "Safe optimization", body: "Reduce prompt waste while protecting code, JSON, and URLs before generation." },
              { icon: Route, title: "Multi-LLM hub", body: "Route across configured providers such as Groq, OpenAI, Gemini, xAI, and Ollama." },
              { icon: BarChart3, title: "Real measurements", body: "Track actual tokens, latency, and estimated cost from live provider responses." },
            ].map((f) => (
              <div
                key={f.title}
                className="rounded-2xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-md p-5 shadow-[0_0_40px_rgba(56,189,248,0.04)]"
              >
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-white/10 flex items-center justify-center mb-3">
                  <f.icon className="w-4 h-4 text-cyan-300" />
                </div>
                <h3 className="text-sm font-semibold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-white/45 leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="mx-auto max-w-6xl px-4 sm:px-6 py-16 scroll-mt-20">
          <SectionHeading
            title="How it works"
            subtitle="One request path from prompt to provider — with visibility at every step."
          />
          <div className="mt-10 grid md:grid-cols-4 gap-4">
            {[
              { step: "01", title: "Analyze", body: "Intent and difficulty signals guide routing expectations." },
              { step: "02", title: "Optimize", body: "Safe, rule-based prompt cleanup when enabled." },
              { step: "03", title: "Route", body: "AUTO selects among providers that can generate live." },
              { step: "04", title: "Measure", body: "Tokens, latency, and cost are recorded from the real call." },
            ].map((s) => (
              <div key={s.step} className="rounded-2xl border border-white/[0.08] bg-[#0B1220]/60 p-5">
                <div className="text-xs font-mono text-violet-300/80 mb-2">{s.step}</div>
                <h3 className="text-sm font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-white/45">{s.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="mx-auto max-w-6xl px-4 sm:px-6 py-16 scroll-mt-20">
          <SectionHeading
            title="Simple workspace plans"
            subtitle="Start exploring SmartLLM Cloud, then scale as your request volume grows."
          />
          <div className="mt-10 grid md:grid-cols-3 gap-4">
            {[
              {
                name: "Starter",
                price: "Free",
                blurb: "Playground, benchmarks, and provider health for evaluation.",
                cta: "Start free",
                featured: false,
              },
              {
                name: "Team",
                price: "Usage-based",
                blurb: "Shared workspace metrics, request history, and multi-provider routing.",
                cta: "Get started",
                featured: true,
              },
              {
                name: "Scale",
                price: "Custom",
                blurb: "Higher volume routing with analytics tailored to your workload.",
                cta: "Talk to us",
                featured: false,
              },
            ].map((p) => (
              <div
                key={p.name}
                className={cn(
                  "rounded-2xl border p-6 flex flex-col",
                  p.featured
                    ? "border-violet-400/40 bg-gradient-to-b from-violet-600/15 to-cyan-600/5 shadow-[0_0_50px_rgba(139,92,246,0.12)]"
                    : "border-white/[0.08] bg-white/[0.03]"
                )}
              >
                <div className="flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-cyan-300" />
                  <h3 className="font-semibold">{p.name}</h3>
                </div>
                <p className="mt-3 text-2xl font-bold tracking-tight">{p.price}</p>
                <p className="mt-2 text-sm text-white/45 flex-1">{p.blurb}</p>
                <Link href="/login" className="mt-6">
                  <Button variant={p.featured ? "primary" : "outline"} className="w-full">
                    {p.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="mx-auto max-w-6xl px-4 sm:px-6 py-16 scroll-mt-20">
          <SectionHeading title="FAQ" subtitle="Quick answers about SmartLLM Cloud." />
          <div className="mt-10 space-y-3 max-w-3xl">
            {[
              {
                q: "Does SmartLLM Cloud replace my LLM providers?",
                a: "No. It sits in front of your configured providers and routes requests using cost, speed, balanced, or quality modes.",
              },
              {
                q: "Are tokens and costs estimated or real?",
                a: "Playground and Benchmark record real provider usage tokens and latency, then compute cost from the centralized catalog pricing.",
              },
              {
                q: "What happens if a provider key is configured but unusable?",
                a: "AUTO routing only considers providers that pass a live usability check, so broken credits or auth failures are skipped.",
              },
              {
                q: "Can I compare Direct LLM vs SmartLLM?",
                a: "Yes — the Benchmark page runs the same prompt through a Direct baseline and the SmartLLM pipeline side by side.",
              },
            ].map((item) => (
              <details
                key={item.q}
                className="group rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4"
              >
                <summary className="cursor-pointer list-none text-sm font-medium text-white/90 flex items-center justify-between gap-3">
                  {item.q}
                  <span className="text-white/30 group-open:rotate-45 transition-transform">+</span>
                </summary>
                <p className="mt-3 text-sm text-white/45 leading-relaxed">{item.a}</p>
              </details>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-white/[0.06] py-8 mt-8">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <Logo showText />
          <p className="text-xs text-white/30">Optimize • Route • Monitor</p>
        </div>
      </footer>
    </div>
  );
}

function SectionHeading({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">{title}</h2>
      <p className="mt-3 text-sm sm:text-base text-white/45">{subtitle}</p>
    </div>
  );
}

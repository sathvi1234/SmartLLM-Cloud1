"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/logo";
import { RobotVisual } from "@/components/robot-visual";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const router = useRouter();

  return (
    <div className="relative min-h-screen text-white overflow-x-hidden">
      <div className="fixed inset-0 -z-10 pointer-events-none" aria-hidden>
        <div className="absolute inset-0 bg-[#070B16]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_80%_40%,rgba(56,189,248,0.14),transparent_55%),radial-gradient(ellipse_45%_40%_at_15%_30%,rgba(139,92,246,0.18),transparent_50%)]" />
      </div>

      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-6">
        <Link href="/" className="inline-flex">
          <Logo showText />
        </Link>
      </div>

      <div className="mx-auto max-w-6xl px-4 sm:px-6 pb-16">
        <div className="grid lg:grid-cols-2 gap-10 lg:gap-12 items-center">
          <div className="w-full max-w-md mx-auto lg:mx-0 order-1">
            <div className="rounded-3xl border border-white/[0.10] bg-white/[0.04] backdrop-blur-xl p-6 sm:p-8 shadow-[0_0_60px_rgba(139,92,246,0.10)] text-center">
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Welcome to SmartLLM Cloud
              </h1>
              <p className="mt-4 text-sm sm:text-base text-white/50 leading-relaxed">
                Experience AI model optimization, cost tracking, analytics, and intelligent LLM provider selection.
              </p>

              <Button
                type="button"
                variant="primary"
                size="lg"
                className="w-full mt-8"
                onClick={() => router.push("/dashboard")}
              >
                🚀 Continue as Demo User
              </Button>

              <p className="mt-4 text-xs text-white/35">Demo User • Demo Pro</p>
            </div>
          </div>

          <div className="order-2 w-full max-w-md mx-auto lg:max-w-none h-[300px] sm:h-[380px] lg:h-[520px]">
            <RobotVisual className="w-full h-full" />
          </div>
        </div>
      </div>
    </div>
  );
}

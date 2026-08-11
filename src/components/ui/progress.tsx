"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  color?: "violet" | "blue" | "emerald" | "amber" | "red";
  size?: "sm" | "md" | "lg";
  animated?: boolean;
  showLabel?: boolean;
}

const colorMap = {
  violet: "bg-violet-500",
  blue: "bg-blue-500",
  emerald: "bg-emerald-500",
  amber: "bg-amber-500",
  red: "bg-red-500",
};

const glowMap = {
  violet: "shadow-[0_0_8px_rgba(139,92,246,0.6)]",
  blue: "shadow-[0_0_8px_rgba(59,130,246,0.6)]",
  emerald: "shadow-[0_0_8px_rgba(16,185,129,0.6)]",
  amber: "shadow-[0_0_8px_rgba(245,158,11,0.6)]",
  red: "shadow-[0_0_8px_rgba(239,68,68,0.6)]",
};

export function Progress({
  value,
  max = 100,
  color = "violet",
  size = "md",
  animated = true,
  showLabel = false,
  className,
  ...props
}: ProgressProps) {
  const pct = Math.min((value / max) * 100, 100);

  return (
    <div className={cn("w-full", className)} {...props}>
      {showLabel && (
        <div className="flex justify-between text-xs text-white/40 mb-1.5">
          <span>{pct.toFixed(0)}%</span>
          <span>
            {value.toLocaleString()} / {max.toLocaleString()}
          </span>
        </div>
      )}
      <div
        className={cn("w-full bg-white/[0.06] rounded-full overflow-hidden", {
          "h-1": size === "sm",
          "h-1.5": size === "md",
          "h-2.5": size === "lg",
        })}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            colorMap[color],
            glowMap[color],
            animated && "animate-none"
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

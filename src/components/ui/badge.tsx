"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-violet-500/15 text-violet-400 border border-violet-500/20",
        success: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20",
        warning: "bg-amber-500/15 text-amber-400 border border-amber-500/20",
        error: "bg-red-500/15 text-red-400 border border-red-500/20",
        info: "bg-blue-500/15 text-blue-400 border border-blue-500/20",
        neutral: "bg-white/5 text-white/60 border border-white/10",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

export function Badge({ className, variant, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span
          className={cn("w-1.5 h-1.5 rounded-full animate-pulse", {
            "bg-violet-400": variant === "default",
            "bg-emerald-400": variant === "success",
            "bg-amber-400": variant === "warning",
            "bg-red-400": variant === "error",
            "bg-blue-400": variant === "info",
            "bg-white/40": variant === "neutral",
          })}
        />
      )}
      {children}
    </span>
  );
}

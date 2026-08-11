"use client";

import * as React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
  hover?: boolean;
  glow?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

export function Card({
  className,
  glass = false,
  hover = false,
  glow = false,
  padding = "md",
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border transition-all duration-300",
        glass
          ? "bg-white/[0.03] border-white/[0.08] backdrop-blur-xl"
          : "bg-[#0F0F1A] border-white/[0.06]",
        hover && "hover:border-white/[0.15] hover:bg-white/[0.05] cursor-pointer",
        glow && "hover:shadow-[0_0_30px_rgba(139,92,246,0.1)]",
        {
          "p-0": padding === "none",
          "p-4": padding === "sm",
          "p-6": padding === "md",
          "p-8": padding === "lg",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

interface AnimatedCardProps extends Omit<HTMLMotionProps<"div">, "children"> {
  children: React.ReactNode;
  glass?: boolean;
  hover?: boolean;
  glow?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
  delay?: number;
  className?: string;
}

export function AnimatedCard({
  className,
  glass = false,
  hover = false,
  glow = false,
  padding = "md",
  delay = 0,
  children,
  ...props
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={hover ? { scale: 1.01, y: -2 } : undefined}
      className={cn(
        "rounded-2xl border transition-colors duration-300",
        glass
          ? "bg-white/[0.03] border-white/[0.08] backdrop-blur-xl"
          : "bg-[#0F0F1A] border-white/[0.06]",
        hover && "hover:border-white/[0.15] cursor-pointer",
        glow && "hover:shadow-[0_0_40px_rgba(139,92,246,0.12)]",
        {
          "p-0": padding === "none",
          "p-4": padding === "sm",
          "p-6": padding === "md",
          "p-8": padding === "lg",
        },
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex items-center justify-between mb-5", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("text-sm font-semibold text-white/90 tracking-tight", className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-xs text-white/40 mt-0.5", className)} {...props}>
      {children}
    </p>
  );
}

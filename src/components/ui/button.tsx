"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 disabled:pointer-events-none disabled:opacity-40 select-none",
  {
    variants: {
      variant: {
        primary: "bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-500/20 active:scale-[0.98]",
        secondary: "bg-white/[0.06] hover:bg-white/[0.10] text-white/80 border border-white/[0.08] hover:border-white/[0.15]",
        ghost: "hover:bg-white/[0.06] text-white/60 hover:text-white/90",
        danger: "bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/20 hover:border-red-500/40",
        outline: "border border-white/[0.12] hover:border-white/[0.25] text-white/70 hover:text-white hover:bg-white/[0.04]",
        glow: "bg-violet-600 hover:bg-violet-500 text-white shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:shadow-[0_0_30px_rgba(139,92,246,0.6)]",
      },
      size: {
        xs: "h-7 px-2.5 text-xs rounded-lg gap-1",
        sm: "h-8 px-3 text-xs",
        md: "h-9 px-4",
        lg: "h-11 px-6 text-base",
        icon: "h-9 w-9",
        "icon-sm": "h-7 w-7 rounded-lg",
      },
    },
    defaultVariants: { variant: "secondary", size: "md" },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          leftIcon
        )}
        {children}
        {!loading && rightIcon}
      </button>
    );
  }
);

Button.displayName = "Button";

export function IconButton({ className, variant = "ghost", size = "icon", ...props }: ButtonProps) {
  return <Button className={cn("rounded-xl", className)} variant={variant} size={size} {...props} />;
}

"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface TooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  side?: "top" | "bottom" | "left" | "right";
  className?: string;
}

export function Tooltip({ children, content, side = "top", className }: TooltipProps) {
  const [open, setOpen] = React.useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  const motionProps = {
    top: { initial: { opacity: 0, y: 4 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 4 } },
    bottom: { initial: { opacity: 0, y: -4 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -4 } },
    left: { initial: { opacity: 0, x: 4 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: 4 } },
    right: { initial: { opacity: 0, x: -4 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: -4 } },
  };

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      {children}
      <AnimatePresence>
        {open && (
          <motion.div
            {...motionProps[side]}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className={cn(
              "absolute z-50 pointer-events-none whitespace-nowrap",
              positionClasses[side],
              className
            )}
          >
            <div className="bg-[#1A1A2E] border border-white/10 text-white/80 text-xs px-2.5 py-1.5 rounded-lg shadow-xl backdrop-blur-xl">
              {content}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

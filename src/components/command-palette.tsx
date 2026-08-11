"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search, LayoutDashboard, Bot, Terminal, LineChart, Database,
  BarChart3, Settings, History, X, ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const commands = [
  { id: "1", label: "Go to Dashboard", icon: LayoutDashboard, category: "Navigation", shortcut: "G O", href: "/dashboard" },
  { id: "2", label: "Open Playground", icon: Terminal, category: "Navigation", shortcut: "G P", href: "/playground" },
  { id: "3", label: "Run Benchmark", icon: LineChart, category: "Navigation", shortcut: "G B", href: "/benchmark" },
  { id: "4", label: "View Models", icon: Database, category: "Navigation", shortcut: "G M", href: "/models" },
  { id: "5", label: "View Agents", icon: Bot, category: "Navigation", shortcut: "G A", href: "/agents" },
  { id: "6", label: "Analytics Dashboard", icon: BarChart3, category: "Navigation", shortcut: "G N", href: "/analytics" },
  { id: "7", label: "Request History", icon: History, category: "Navigation", shortcut: "G H", href: "/history" },
  { id: "8", label: "Settings", icon: Settings, category: "Settings", shortcut: "⌘ ,", href: "/settings" },
];

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const runCommand = (href: string) => {
    onClose();
    router.push(href);
  };

  const filtered = commands.filter(
    (c) =>
      c.label.toLowerCase().includes(query.toLowerCase()) ||
      c.category.toLowerCase().includes(query.toLowerCase())
  );

  const grouped = filtered.reduce(
    (acc, cmd) => {
      if (!acc[cmd.category]) acc[cmd.category] = [];
      acc[cmd.category].push(cmd);
      return acc;
    },
    {} as Record<string, typeof commands>
  );

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery("");
      setSelected(0);
    }
  }, [open]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (!open) return;
      if (e.key === "ArrowDown") { e.preventDefault(); setSelected((s) => Math.min(s + 1, filtered.length - 1)); }
      if (e.key === "ArrowUp") { e.preventDefault(); setSelected((s) => Math.max(s - 1, 0)); }
      if (e.key === "Enter") {
        e.preventDefault();
        const cmd = filtered[selected];
        if (cmd) runCommand(cmd.href);
      }
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, filtered, selected, onClose]);

  let itemIndex = 0;

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.96, y: -16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: -16 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="pointer-events-auto w-full max-w-xl bg-[#0D0D1A]/95 border border-white/[0.10] rounded-2xl shadow-2xl shadow-black/50 backdrop-blur-2xl overflow-hidden"
            >
              {/* Search Input */}
              <div className="flex items-center gap-3 px-4 py-4 border-b border-white/[0.06]">
                <Search className="w-4 h-4 text-white/30 shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => { setQuery(e.target.value); setSelected(0); }}
                  placeholder="Search commands, agents, workflows..."
                  className="flex-1 bg-transparent text-sm text-white placeholder:text-white/25 outline-none"
                />
                {query && (
                  <button onClick={() => setQuery("")} className="text-white/30 hover:text-white/60 transition-colors">
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
                <kbd className="hidden sm:flex items-center gap-1 text-[10px] text-white/20 bg-white/[0.05] border border-white/[0.08] rounded px-1.5 py-0.5">
                  ESC
                </kbd>
              </div>

              {/* Commands */}
              <div className="max-h-80 overflow-y-auto overscroll-contain py-2">
                {Object.entries(grouped).length === 0 ? (
                  <div className="py-10 text-center">
                    <p className="text-sm text-white/25">No commands found</p>
                  </div>
                ) : (
                  Object.entries(grouped).map(([category, items]) => (
                    <div key={category}>
                      <div className="px-4 py-2">
                        <span className="text-[10px] font-semibold text-white/25 uppercase tracking-widest">
                          {category}
                        </span>
                      </div>
                      {items.map((cmd) => {
                        const idx = itemIndex++;
                        const isSelected = idx === selected;
                        const Icon = cmd.icon;
                        return (
                          <motion.button
                            key={cmd.id}
                            whileTap={{ scale: 0.99 }}
                            onClick={() => runCommand(cmd.href)}
                            className={cn(
                              "w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors group",
                              isSelected ? "bg-violet-500/10 text-white" : "text-white/60 hover:bg-white/[0.04] hover:text-white/90"
                            )}
                          >
                            <div className={cn(
                              "w-7 h-7 rounded-lg flex items-center justify-center transition-colors",
                              isSelected ? "bg-violet-500/20" : "bg-white/[0.05] group-hover:bg-white/[0.08]"
                            )}>
                              <Icon className="w-3.5 h-3.5" />
                            </div>
                            <span className="flex-1">{cmd.label}</span>
                            {cmd.shortcut && (
                              <kbd className="text-[10px] text-white/20 bg-white/[0.05] border border-white/[0.08] rounded px-1.5 py-0.5">
                                {cmd.shortcut}
                              </kbd>
                            )}
                            <ArrowRight className={cn("w-3.5 h-3.5 transition-opacity", isSelected ? "opacity-60" : "opacity-0 group-hover:opacity-30")} />
                          </motion.button>
                        );
                      })}
                    </div>
                  ))
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center gap-4 px-4 py-2.5 border-t border-white/[0.06]">
                {[["↑↓", "Navigate"], ["↵", "Select"], ["ESC", "Close"]].map(([key, label]) => (
                  <div key={key} className="flex items-center gap-1.5">
                    <kbd className="text-[10px] text-white/25 bg-white/[0.05] border border-white/[0.08] rounded px-1.5 py-0.5">{key}</kbd>
                    <span className="text-[10px] text-white/20">{label}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

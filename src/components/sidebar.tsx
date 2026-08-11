"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  LayoutDashboard, Bot, BarChart3, Settings,
  Search, ChevronRight, Command, Database,
  Terminal, LineChart, History
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Logo } from "@/components/logo";

const navItems: Array<{
  id: string; label: string; icon: React.ComponentType<{ className?: string }>;
  href: string; shortcut?: string; badge?: number;
}> = [
  { id: "overview", label: "Dashboard", icon: LayoutDashboard, href: "/dashboard", shortcut: "G O" },
  { id: "playground", label: "Playground", icon: Terminal, href: "/playground", shortcut: "G P" },
  { id: "benchmark", label: "Benchmark", icon: LineChart, href: "/benchmark", shortcut: "G B" },
  { id: "models", label: "Models", icon: Database, href: "/models", shortcut: "G M" },
  { id: "agents", label: "Agents", icon: Bot, href: "/agents", shortcut: "G A" },
  { id: "analytics", label: "Analytics", icon: BarChart3, href: "/analytics", shortcut: "G N" },
  { id: "history", label: "Request History", icon: History, href: "/history", shortcut: "G H" },
];

const bottomItems = [
  { id: "settings", label: "Settings", icon: Settings, href: "/settings", shortcut: "⌘," },
];

interface SidebarProps {
  activeItem?: string;
  onCommandPalette?: () => void;
}

export function Sidebar({ activeItem = "overview", onCommandPalette }: SidebarProps) {
  const [expanded, setExpanded] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <>
      {/* Overlay for mobile */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-30 lg:hidden"
            onClick={() => setExpanded(false)}
          />
        )}
      </AnimatePresence>

      <motion.aside
        initial={false}
        animate={{ width: expanded ? 240 : 64 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="fixed left-0 top-0 h-full z-40 flex flex-col bg-[#08080F] border-r border-white/[0.06] overflow-hidden"
      >
        {/* Logo / branding — mark + wordmark only; sidebar chrome unchanged */}
        <div className="h-16 flex items-center px-4 border-b border-white/[0.06] shrink-0">
          <AnimatePresence mode="wait" initial={false}>
            {expanded ? (
              <motion.div
                key="logo-expanded"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.2 }}
                className="min-w-0"
              >
                <Logo showText />
              </motion.div>
            ) : (
              <motion.div
                key="logo-collapsed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              >
                <Logo />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="absolute top-[68px] -right-3 w-6 h-6 bg-[#0F0F1A] border border-white/[0.10] rounded-full flex items-center justify-center text-white/40 hover:text-white/80 transition-colors shadow-lg z-50"
        >
          <motion.div animate={{ rotate: expanded ? 0 : 180 }} transition={{ duration: 0.2 }}>
            <ChevronRight className="w-3 h-3" />
          </motion.div>
        </button>

        {/* Command Palette Trigger */}
        <div className="px-3 pt-3 pb-1">
          <Tooltip content="Command Palette (⌘K)" side="right">
            <button
              onClick={onCommandPalette}
              className={cn(
                "w-full flex items-center gap-2.5 h-8 rounded-xl transition-all duration-200",
                "bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] hover:border-white/[0.12]",
                expanded ? "px-3" : "justify-center px-0"
              )}
            >
              <Search className="w-3.5 h-3.5 text-white/30 shrink-0" />
              <AnimatePresence>
                {expanded && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex-1 flex items-center justify-between"
                  >
                    <span className="text-xs text-white/25">Search...</span>
                    <kbd className="flex items-center gap-0.5 text-[9px] text-white/20 bg-white/[0.04] border border-white/[0.08] rounded px-1 py-0.5">
                      <Command className="w-2.5 h-2.5" /> K
                    </kbd>
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          </Tooltip>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-2 space-y-0.5 overflow-y-auto overflow-x-hidden">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeItem === item.id;
            return (
              <Tooltip key={item.id} content={`${item.label}${item.shortcut ? ` (${item.shortcut})` : ""}`} side="right">
                <Link
                  href={item.href}
                  className={cn(
                    "relative flex items-center gap-3 h-9 rounded-xl transition-all duration-200 group",
                    expanded ? "px-3" : "justify-center px-0",
                    isActive
                      ? "bg-violet-500/15 text-violet-300"
                      : "text-white/40 hover:text-white/80 hover:bg-white/[0.05]"
                  )}
                >
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-violet-400 rounded-full"
                    />
                  )}
                  <Icon className="w-4 h-4 shrink-0" />
                  <AnimatePresence>
                    {expanded && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="text-sm font-medium flex-1 whitespace-nowrap"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                  {item.badge && (
                    <AnimatePresence>
                      {expanded ? (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                          <Badge variant="default" className="text-[10px] h-4 px-1.5">
                            {item.badge}
                          </Badge>
                        </motion.div>
                      ) : (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          className="absolute top-1.5 right-1.5 w-2 h-2 bg-violet-400 rounded-full"
                        />
                      )}
                    </AnimatePresence>
                  )}
                </Link>
              </Tooltip>
            );
          })}
        </nav>

        {/* Divider */}
        <div className="mx-3 h-px bg-white/[0.06]" />

        {/* Bottom Nav */}
        <nav className="px-3 py-3 space-y-0.5">
          {bottomItems.map((item) => {
            const Icon = item.icon;
            return (
              <Tooltip key={item.id} content={item.label} side="right">
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 h-9 rounded-xl text-white/35 hover:text-white/70 hover:bg-white/[0.04] transition-all duration-200",
                    expanded ? "px-3" : "justify-center px-0"
                  )}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <AnimatePresence>
                    {expanded && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="text-sm font-medium whitespace-nowrap"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </Link>
              </Tooltip>
            );
          })}
        </nav>

        {/* User Avatar */}
        <div className="px-3 py-3 border-t border-white/[0.06]">
          <div className={cn("flex items-center gap-3 rounded-xl p-2 hover:bg-white/[0.04] transition-colors cursor-pointer", !expanded && "justify-center")}>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-blue-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
              AK
            </div>
            <AnimatePresence>
              {expanded && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-w-0">
                  <div className="text-xs font-semibold text-white/80 truncate">Aryan K.</div>
                  <div className="text-[10px] text-white/30 truncate">Pro Plan</div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.aside>
    </>
  );
}

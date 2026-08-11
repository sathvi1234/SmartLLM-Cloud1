"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Bell, Search, Plus, RefreshCw, Sparkles, ChevronDown, Command } from "lucide-react";
import { Button, IconButton } from "@/components/ui/button";
import { Tooltip } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface HeaderProps {
  title: string;
  subtitle?: string;
  onCommandPalette?: () => void;
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, onCommandPalette, actions }: HeaderProps) {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise((r) => setTimeout(r, 1200));
    setRefreshing(false);
  };

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-16 px-6 bg-[#09090F]/80 backdrop-blur-xl border-b border-white/[0.06]">
      {/* Left */}
      <div className="flex items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-white tracking-tight">{title}</h1>
            {subtitle && (
              <>
                <span className="text-white/20">/</span>
                <span className="text-sm text-white/40">{subtitle}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        {actions}

        <Tooltip content="Refresh data (R)">
          <IconButton
            variant="ghost"
            onClick={handleRefresh}
            aria-label="Refresh"
          >
            <RefreshCw className={cn("w-4 h-4 text-white/40", refreshing && "animate-spin text-violet-400")} />
          </IconButton>
        </Tooltip>

        <Tooltip content="Notifications">
          <div className="relative">
            <IconButton variant="ghost" aria-label="Notifications">
              <Bell className="w-4 h-4 text-white/40" />
            </IconButton>
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-violet-400 rounded-full" />
          </div>
        </Tooltip>

        <div className="h-5 w-px bg-white/[0.08] mx-1" />

        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus className="w-3.5 h-3.5" />}
          className="shadow-lg shadow-violet-500/20"
        >
          Deploy Agent
        </Button>
      </div>
    </header>
  );
}

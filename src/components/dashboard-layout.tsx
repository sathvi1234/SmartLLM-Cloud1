"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "@/components/sidebar";
import { CommandPalette } from "@/components/command-palette";

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeItem?: string;
}

export default function DashboardLayout({ children, activeItem = "overview" }: DashboardLayoutProps) {
  const [commandOpen, setCommandOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className="relative min-h-screen text-white">
      {/* Background-only layer: HUD image + overlay; never intercepts pointer events */}
      <div className="app-hud-bg" aria-hidden>
        <div className="app-hud-bg__image" />
        <div className="app-hud-bg__overlay" />
        <div className="app-hud-bg__glow" />
      </div>

      <div className="relative z-10">
        <Sidebar activeItem={activeItem} onCommandPalette={() => setCommandOpen(true)} />

        {/* Main content offset for sidebar */}
        <div className="pl-16 min-h-screen flex flex-col">
          {children}
        </div>

        <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
      </div>
    </div>
  );
}

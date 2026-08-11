"use client";

import React, { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

export type RobotMood = "idle" | "email" | "password" | "typing";

interface RobotVisualProps {
  className?: string;
  mood?: RobotMood;
  /** Enable light mouse parallax on the robot group */
  enableParallax?: boolean;
}

/**
 * Original SmartLLM Cloud AI assistant mark (SVG).
 * Inspired by friendly multi-LLM assistant concepts — not a copy of third-party art.
 */
export function RobotVisual({
  className,
  mood = "idle",
  enableParallax = true,
}: RobotVisualProps) {
  const reduceMotion = useReducedMotion();
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (reduceMotion || !enableParallax) return;
    const onMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 12;
      const y = (e.clientY / window.innerHeight - 0.5) * 8;
      setOffset({ x, y });
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, [reduceMotion, enableParallax]);

  const eyeOpen = mood === "password" ? 2.2 : 4.2;
  const coreGlow =
    mood === "email" ? 0.95 : mood === "typing" ? 1 : mood === "password" ? 0.55 : 0.75;
  const chipLift = mood === "typing" ? -6 : mood === "email" ? -3 : 0;

  return (
    <div className={cn("relative select-none pointer-events-none", className)} aria-hidden>
      {/* Soft ambient glow */}
      <div
        className={cn(
          "absolute inset-[12%] rounded-full bg-cyan-400/10 blur-3xl",
          !reduceMotion && "animate-pulse"
        )}
        style={{ opacity: coreGlow }}
      />

      <motion.div
        animate={
          reduceMotion
            ? { x: 0, y: 0 }
            : { x: offset.x, y: [offset.y - 6, offset.y + 6, offset.y - 6] }
        }
        transition={
          reduceMotion
            ? { duration: 0 }
            : { y: { duration: 5.5, repeat: Infinity, ease: "easeInOut" }, x: { duration: 0.4 } }
        }
        className="relative w-full h-full"
      >
        <svg viewBox="0 0 320 420" className="w-full h-full drop-shadow-[0_20px_60px_rgba(56,189,248,0.25)]">
          <defs>
            <linearGradient id="slm-bot-body" x1="60" y1="40" x2="260" y2="380" gradientUnits="userSpaceOnUse">
              <stop stopColor="#F8FAFC" />
              <stop offset="0.55" stopColor="#E2E8F0" />
              <stop offset="1" stopColor="#CBD5E1" />
            </linearGradient>
            <linearGradient id="slm-bot-accent" x1="0" y1="0" x2="1" y2="1">
              <stop stopColor="#22D3EE" />
              <stop offset="0.5" stopColor="#818CF8" />
              <stop offset="1" stopColor="#A855F7" />
            </linearGradient>
            <radialGradient id="slm-bot-core" cx="50%" cy="50%" r="50%">
              <stop stopColor="#67E8F9" stopOpacity="1" />
              <stop offset="1" stopColor="#7C3AED" stopOpacity="0.2" />
            </radialGradient>
            <filter id="slm-bot-glow" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="4" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Circuit floor ring */}
          <ellipse cx="160" cy="390" rx="110" ry="18" fill="#22D3EE" fillOpacity="0.08" />
          <ellipse cx="160" cy="390" rx="90" ry="12" fill="none" stroke="url(#slm-bot-accent)" strokeOpacity="0.35" strokeWidth="1.5" strokeDasharray="4 6" />

          {/* Legs */}
          <rect x="118" y="290" width="28" height="70" rx="14" fill="url(#slm-bot-body)" />
          <rect x="174" y="290" width="28" height="70" rx="14" fill="url(#slm-bot-body)" />
          <circle cx="132" cy="300" r="12" fill="url(#slm-bot-accent)" opacity="0.85" />
          <circle cx="188" cy="300" r="12" fill="url(#slm-bot-accent)" opacity="0.85" />
          <ellipse cx="132" cy="365" rx="20" ry="10" fill="#F1F5F9" />
          <ellipse cx="188" cy="365" rx="20" ry="10" fill="#F1F5F9" />

          {/* Torso */}
          <path
            d="M100 165c0-18 20-32 60-32s60 14 60 32v95c0 28-24 48-60 48s-60-20-60-48V165z"
            fill="url(#slm-bot-body)"
          />
          <circle cx="160" cy="220" r="22" fill="url(#slm-bot-core)" filter="url(#slm-bot-glow)" opacity={coreGlow} />
          <circle cx="160" cy="220" r="10" fill="#ECFEFF" opacity="0.9" />

          {/* Arms */}
          <path d="M98 180c-28 10-42 40-38 70 2 12 14 20 26 16l8-4c-6-18 2-40 18-52l-14-30z" fill="url(#slm-bot-body)" />
          <circle cx="72" cy="248" r="11" fill="url(#slm-bot-accent)" />
          {/* Presenting hand (right from viewer = robot left) */}
          <path d="M222 180c28 8 48 36 46 68-1 14-14 22-27 18l-8-3c4-20-6-42-24-52l13-31z" fill="url(#slm-bot-body)" />
          <circle cx="248" cy="245" r="11" fill="url(#slm-bot-accent)" />
          <ellipse cx="268" cy="262" rx="22" ry="12" fill="#F8FAFC" transform="rotate(-18 268 262)" />

          {/* Head */}
          <rect x="118" y="70" width="84" height="78" rx="36" fill="url(#slm-bot-body)" />
          <rect x="128" y="92" width="64" height="36" rx="18" fill="#0F172A" />
          {/* Eyes */}
          <rect x="140" y={110 - eyeOpen / 2} width="14" height={eyeOpen} rx="3" fill="#F8FAFC" filter="url(#slm-bot-glow)" />
          <rect x="166" y={110 - eyeOpen / 2} width="14" height={eyeOpen} rx="3" fill="#F8FAFC" filter="url(#slm-bot-glow)" />
          {/* Ear nodes */}
          <circle cx="118" cy="110" r="8" fill="url(#slm-bot-accent)" />
          <circle cx="202" cy="110" r="8" fill="url(#slm-bot-accent)" />

          {/* Floating AI chip above palm */}
          <g transform={`translate(0 ${chipLift})`} filter="url(#slm-bot-glow)">
            {!reduceMotion && (
              <circle cx="275" cy="210" r="28" fill="none" stroke="#67E8F9" strokeOpacity="0.25" strokeWidth="1" strokeDasharray="3 5">
                <animateTransform attributeName="transform" type="rotate" from="0 275 210" to="360 275 210" dur="18s" repeatCount="indefinite" />
              </circle>
            )}
            <rect x="252" y="188" width="46" height="46" rx="10" fill="#0B1220" stroke="url(#slm-bot-accent)" strokeWidth="2" />
            <text x="275" y="217" textAnchor="middle" fill="#E0F2FE" fontSize="16" fontWeight="700" fontFamily="ui-sans-serif,system-ui">
              AI
            </text>
            {/* Orbit particles */}
            <circle cx="275" cy="178" r="2.5" fill="#22D3EE">
              {!reduceMotion && (
                <animateTransform attributeName="transform" type="rotate" from="0 275 211" to="360 275 211" dur="8s" repeatCount="indefinite" />
              )}
            </circle>
            <circle cx="300" cy="220" r="2" fill="#A855F7">
              {!reduceMotion && (
                <animateTransform attributeName="transform" type="rotate" from="90 275 211" to="450 275 211" dur="11s" repeatCount="indefinite" />
              )}
            </circle>
          </g>

          {/* Privacy shield hint when password focused */}
          {mood === "password" && (
            <g opacity="0.85">
              <path d="M160 198l18 8v14c0 12-8 22-18 26-10-4-18-14-18-26v-14l18-8z" fill="none" stroke="#A855F7" strokeWidth="2" />
            </g>
          )}
        </svg>
      </motion.div>
    </div>
  );
}

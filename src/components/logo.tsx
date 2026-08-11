import React from "react";
import { cn } from "@/lib/utils";

/**
 * SmartLLM Cloud brand mark: central AI brain/circuit with connected model nodes.
 * Abstract multi-LLM hub — not OpenAI / Gemini / Groq / xAI branding.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0", className)}
      aria-hidden
    >
      <defs>
        <linearGradient id="slm-brain" x1="8" y1="10" x2="32" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#22D3EE" />
          <stop offset="0.45" stopColor="#818CF8" />
          <stop offset="1" stopColor="#A855F7" />
        </linearGradient>
        <linearGradient id="slm-node" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#67E8F9" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
        <filter id="slm-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="0.6" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Orbital rings */}
      <circle cx="20" cy="20" r="15.5" stroke="#67E8F9" strokeOpacity="0.22" strokeWidth="0.6" strokeDasharray="2 2.5" />
      <circle cx="20" cy="20" r="12.2" stroke="#A855F7" strokeOpacity="0.18" strokeWidth="0.5" strokeDasharray="1.5 2" />

      {/* Spoke lines to model nodes */}
      <g stroke="url(#slm-node)" strokeOpacity="0.55" strokeWidth="0.7" strokeDasharray="1.2 1.4">
        <path d="M14.2 14.2 L8.5 8.5" />
        <path d="M25.8 14.2 L31.5 8.5" />
        <path d="M14.2 25.8 L8.5 31.5" />
        <path d="M25.8 25.8 L31.5 31.5" />
      </g>

      {/* Central brain / circuit hub */}
      <g filter="url(#slm-glow)">
        <path
          d="M20 11.2c-2.1 0-3.7 1.1-4.5 2.3-.7-.4-1.6-.5-2.5-.2-1.6.6-2.4 2.3-2.1 4 .2 1.1.9 2 1.8 2.5-.1.5-.1 1 0 1.5.3 1.8 1.7 3.1 3.4 3.6.7 1.4 2.1 2.4 3.9 2.4s3.2-1 3.9-2.4c1.7-.5 3.1-1.8 3.4-3.6.1-.5.1-1 0-1.5.9-.5 1.6-1.4 1.8-2.5.3-1.7-.5-3.4-2.1-4-.9-.3-1.8-.2-2.5.2-.8-1.2-2.4-2.3-4.5-2.3z"
          fill="url(#slm-brain)"
          fillOpacity="0.95"
        />
        {/* Circuit traces inside brain */}
        <g stroke="#0B1220" strokeWidth="0.55" strokeLinecap="round" opacity="0.55">
          <path d="M15.2 18.5h3.2M18.4 18.5v3.2M18.4 21.7h2.4" />
          <path d="M21.2 16.8h3.4M24.6 16.8v2.8M22.4 19.6h2.2" />
          <path d="M17.6 23.8h4.8" />
          <circle cx="15.2" cy="18.5" r="0.55" fill="#0B1220" stroke="none" />
          <circle cx="20.8" cy="21.7" r="0.55" fill="#0B1220" stroke="none" />
          <circle cx="24.6" cy="19.6" r="0.55" fill="#0B1220" stroke="none" />
          <circle cx="22.4" cy="23.8" r="0.55" fill="#0B1220" stroke="none" />
        </g>
        {/* Hemisphere divider */}
        <path d="M20 13.4v12.4" stroke="#0B1220" strokeOpacity="0.25" strokeWidth="0.5" />
      </g>

      {/* Satellite model nodes (generic — multi-LLM hub) */}
      <g>
        <circle cx="8.5" cy="8.5" r="3.1" fill="#111827" stroke="url(#slm-node)" strokeWidth="0.8" />
        <path d="M7.3 8.5h2.4M8.5 7.3v2.4" stroke="#E0F2FE" strokeWidth="0.7" strokeLinecap="round" />

        <circle cx="31.5" cy="8.5" r="3.1" fill="#1E1B4B" stroke="#A855F7" strokeWidth="0.8" />
        <text x="31.5" y="9.7" textAnchor="middle" fill="#F5F3FF" fontSize="3.2" fontWeight="700" fontFamily="system-ui,sans-serif">AI</text>

        <circle cx="8.5" cy="31.5" r="3.1" fill="#0C4A6E" stroke="#22D3EE" strokeWidth="0.8" />
        <path d="M8.5 29.9l.55 1.1 1.2.18-.87.85.2 1.2L8.5 32.7l-1.08.53.2-1.2-.87-.85 1.2-.18z" fill="#E0F2FE" />

        <circle cx="31.5" cy="31.5" r="3.1" fill="#1F2937" stroke="#818CF8" strokeWidth="0.8" />
        <circle cx="31.5" cy="31.5" r="1.15" stroke="#E0E7FF" strokeWidth="0.65" />
        <circle cx="31.5" cy="31.5" r="0.35" fill="#E0E7FF" />
      </g>
    </svg>
  );
}

interface LogoProps {
  /** Show wordmark + tagline beside the mark */
  showText?: boolean;
  className?: string;
  markClassName?: string;
}

export function Logo({ showText = false, className, markClassName }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-3 min-w-0", className)}>
      <div
        className={cn(
          "w-8 h-8 rounded-xl flex items-center justify-center shrink-0",
          "bg-gradient-to-br from-cyan-500/20 via-violet-500/25 to-fuchsia-600/20",
          "ring-1 ring-white/10 shadow-lg shadow-violet-500/25",
          markClassName
        )}
      >
        <LogoMark className="w-[26px] h-[26px]" />
      </div>
      {showText && (
        <div className="min-w-0">
          <div className="text-sm font-bold text-white tracking-tight leading-tight">
            SmartLLM Cloud
          </div>
          <div className="text-[10px] text-white/30 font-medium leading-tight mt-0.5 truncate">
            Optimize • Route • Monitor
          </div>
        </div>
      )}
    </div>
  );
}

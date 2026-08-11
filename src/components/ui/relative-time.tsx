"use client";

import React, { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";

interface RelativeTimeProps {
  date: Date | string | number;
  addSuffix?: boolean;
  className?: string;
}

/**
 * Hydration-safe relative timestamp. Relative times ("5 minutes ago") differ
 * between the server-rendered HTML and the client hydration pass, so we render
 * a deterministic placeholder first and only compute the relative time after
 * mount, then keep it fresh with an interval. Server and initial client markup
 * are identical, so no hydration mismatch occurs (and nothing is suppressed).
 */
export function RelativeTime({ date, addSuffix = true, className }: RelativeTimeProps) {
  const [label, setLabel] = useState<string | null>(null);

  useEffect(() => {
    const update = () => setLabel(formatDistanceToNow(new Date(date), { addSuffix }));
    update();
    const id = setInterval(update, 30_000);
    return () => clearInterval(id);
  }, [date, addSuffix]);

  return <span className={className}>{label ?? "…"}</span>;
}

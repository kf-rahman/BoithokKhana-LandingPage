"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/api";

type Status = "checking" | "ok" | "down";

const LABELS: Record<Status, string> = {
  checking: "Checking backend…",
  ok: "Backend reachable",
  down: "Backend unreachable",
};

export default function HealthStatus() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
        if (!cancelled) setStatus(res.ok ? "ok" : "down");
      } catch {
        if (!cancelled) setStatus("down");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <span className="health-pill">
      <span className={`health-dot ${status}`} />
      {LABELS[status]}
    </span>
  );
}

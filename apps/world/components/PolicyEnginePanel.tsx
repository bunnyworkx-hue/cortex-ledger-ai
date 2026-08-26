"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ToolDefinition } from "@/lib/api";

// §17's Policy Engine room, built from real data rather than invented:
// the risk ladder and the threshold are real (PolicyEngine's actual
// configured value, apps/api/axiom_api/main.py:
// PolicyEngine(approval_threshold="high") — not fetched, since no
// endpoint exposes it; stated here as a fixed, documented fact rather
// than silently assumed live), and the tier counts are the real live
// distribution across all 12 registered tools (GET /v1/tools), not
// invented examples. Every real approval's own `reason` text already
// says this in words ("...is risk_level='high', at or above the
// approval threshold...") — this panel is that same real rule made
// visible on its own, tying together what Tool Registry and Human
// Approval each only show a slice of.
const RISK_TIERS = ["low", "medium", "high", "critical"] as const;
const THRESHOLD: (typeof RISK_TIERS)[number] = "high";

export function PolicyEnginePanel() {
  const [open, setOpen] = useState(false);
  const [tools, setTools] = useState<ToolDefinition[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || tools !== null) return;
    let cancelled = false;
    api
      .listTools()
      .then((list) => {
        if (!cancelled) setTools(list);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Could not reach the Axiom API");
      });
    return () => {
      cancelled = true;
    };
  }, [open, tools]);

  const counts = RISK_TIERS.reduce<Record<string, number>>((acc, tier) => {
    acc[tier] = tools?.filter((t) => t.risk_level === tier).length ?? 0;
    return acc;
  }, {});
  const thresholdIndex = RISK_TIERS.indexOf(THRESHOLD);

  return (
    <div className="policy-engine">
      <button className="policy-engine-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        Policy Engine
      </button>

      {open && (
        <div className="policy-engine-panel">
          <div className="policy-engine-head">
            One real rule, applied to every real tool call: risk at or above{" "}
            <strong>{THRESHOLD}</strong> stops for a human; below it runs immediately.
          </div>
          {error && <div className="policy-engine-error">{error}</div>}
          {!tools && !error && <div className="policy-engine-loading">loading live registry…</div>}

          {tools && (
            <div className="policy-ladder">
              {RISK_TIERS.map((tier, i) => (
                <div key={tier} className={`policy-tier policy-tier-${tier}`}>
                  <div className="policy-tier-row">
                    <span className="policy-tier-name">{tier}</span>
                    <span className="policy-tier-count">{counts[tier]} tool{counts[tier] === 1 ? "" : "s"}</span>
                    <span className="policy-tier-outcome">
                      {i >= thresholdIndex ? "requires approval" : "auto-runs"}
                    </span>
                  </div>
                  {i === thresholdIndex && <div className="policy-threshold-line">threshold — configured, not adjustable here</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import { api, ApiError, type AgentRecord } from "@/lib/api";

// The real interactivity gap the 3D scene had: agent points were purely
// decorative, no hover, no click. AgentFabricZone now emits real
// pointer events per real agent; this card is where clicking one leads
// — real fields from the real AgentRecord, and a real "run this" action
// through the same api.delegate() every other panel uses. Kept as its
// own local busy/result state rather than feeding into Talk-Back's
// activeAgentIds (that Set is owned by Talk-Back's own `running`-driven
// effect, which replaces the whole Set on change — a second independent
// writer would race it and stomp its entries).
export function SelectedAgentCard({ agent, onClose }: { agent: AgentRecord; onClose: () => void }) {
  const [task, setTask] = useState("In one sentence, what do you do?");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ text: string; isError: boolean } | null>(null);

  async function run() {
    setBusy(true);
    setResult(null);
    try {
      const response = await api.delegate(agent.agent_id, task);
      setResult({
        text: response.content ? `via ${response.backend_name}: ${response.content}` : `${response.status}.`,
        isError: false,
      });
    } catch (err) {
      setResult({ text: err instanceof ApiError ? err.message : "Could not reach the Axiom API", isError: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="selected-agent">
      <div className="selected-agent-head">
        <div>
          <div className="selected-agent-name">{agent.name}</div>
          <div className="selected-agent-meta">
            {agent.division} · {agent.category}
            {agent.risk_level && <span className={`selected-agent-risk selected-agent-risk-${agent.risk_level}`}>{agent.risk_level}</span>}
          </div>
        </div>
        <button className="selected-agent-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      <div className="selected-agent-description">{agent.description}</div>

      <div className="selected-agent-run">
        <input value={task} onChange={(e) => setTask(e.target.value)} disabled={busy} />
        <button onClick={run} disabled={busy || !task.trim()}>
          {busy ? "…" : "Run"}
        </button>
      </div>
      {result && <div className={`selected-agent-result ${result.isError ? "selected-agent-result-error" : ""}`}>{result.text}</div>}
    </div>
  );
}

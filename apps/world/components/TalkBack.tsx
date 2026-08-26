"use client";

import { useState } from "react";
import { api, ApiError, type AgentRecord } from "@/lib/api";
import { scrollToZone, zoneIdForQuery } from "@/lib/scrollBridge";

type LogEntry =
  | { role: "user"; text: string }
  | { role: "axiom"; text: string; agents?: AgentRecord[] }
  | { role: "error"; text: string };

export function TalkBack() {
  const [open, setOpen] = useState(true);
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState<LogEntry[]>([
    {
      role: "axiom",
      text: 'Search matches literal words in each agent\'s real description — try "security" or "frontend" or "sales analyst". A matching query also jumps the camera to the right zone. Once you see an agent below, click it to actually delegate.',
    },
  ]);

  async function handleSubmit(query: string) {
    if (!query.trim() || busy) return;
    setLog((l) => [...l, { role: "user", text: query }]);
    setValue("");
    setBusy(true);

    const zoneId = zoneIdForQuery(query);
    if (zoneId) scrollToZone(zoneId);

    try {
      const matches = await api.agentFabricSearch(query);
      if (matches.length === 0) {
        setLog((l) => [...l, { role: "axiom", text: "No agents matched that in the real registry — try different wording." }]);
      } else {
        setLog((l) => [
          ...l,
          {
            role: "axiom",
            text: `Found ${matches.length} real agent${matches.length === 1 ? "" : "s"} in the registry${zoneId ? ` — moved to ${zoneId.replace("-", " ")}` : ""}:`,
            agents: matches,
          },
        ]);
      }
    } catch (err) {
      setLog((l) => [...l, { role: "error", text: err instanceof ApiError ? err.message : "Could not reach the Axiom API." }]);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelegate(agent: AgentRecord, task: string) {
    setBusy(true);
    setLog((l) => [...l, { role: "user", text: `run ${agent.agent_id}: ${task}` }]);
    try {
      const result = await api.delegate(agent.agent_id, task);
      setLog((l) => [
        ...l,
        {
          role: "axiom",
          text: result.content
            ? `${agent.name} (${result.backend_name}): ${result.content}`
            : `Execution ${result.execution_id} ${result.status}.`,
        },
      ]);
    } catch (err) {
      setLog((l) => [...l, { role: "error", text: err instanceof ApiError ? err.message : "Delegation failed to reach the API." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="talkback">
      <button className="talkback-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        {open ? "Hide console" : "Ask Axiom"}
      </button>

      {open && (
        <div className="talkback-panel">
          <div className="talkback-log">
            {log.map((entry, i) => (
              <div key={i} className={`talkback-entry talkback-${entry.role}`}>
                <span className="talkback-role">{entry.role === "user" ? "you" : entry.role === "error" ? "!" : "axiom"}</span>
                <div className="talkback-text">
                  {entry.text}
                  {"agents" in entry && entry.agents && (
                    <div className="talkback-agents">
                      {entry.agents.map((agent) => (
                        <button
                          key={agent.agent_id}
                          className="talkback-agent-chip"
                          disabled={busy}
                          onClick={() => handleDelegate(agent, "In one sentence, what do you do?")}
                          title={agent.description}
                        >
                          {agent.name} <span className="talkback-agent-division">{agent.division}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <form
            className="talkback-form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(value);
            }}
          >
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="Ask Axiom anything…"
              disabled={busy}
              aria-label="Command Axiom"
            />
            <button type="submit" disabled={busy || !value.trim()}>
              {busy ? "…" : "Send"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

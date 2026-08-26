"use client";

import { useState } from "react";
import { api, ApiError, type AgentRecord } from "@/lib/api";
import { scrollToZone, zoneIdForQuery } from "@/lib/scrollBridge";

type LogEntry =
  | { role: "user"; text: string }
  | { role: "axiom"; text: string; agents?: AgentRecord[]; task?: string }
  | { role: "result"; text: string; agentId: string }
  | { role: "error"; text: string };

export function TalkBack({
  onActiveAgentsChange,
  onMatchedAgentsChange,
  onExecutingChange,
}: {
  onActiveAgentsChange: (ids: Set<string>) => void;
  onMatchedAgentsChange: (ids: Set<string>) => void;
  onExecutingChange: (executing: boolean) => void;
}) {
  const [open, setOpen] = useState(true);
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [running, setRunning] = useState<Set<string>>(new Set());
  const [log, setLog] = useState<LogEntry[]>([
    {
      role: "axiom",
      text: 'Tell me what you need done — I\'ll find the real agent and run it. Try "who can help with security" or "run a frontend accessibility review". Search matches literal words in each agent\'s real description.',
    },
  ]);

  function markRunning(ids: string[], value: boolean) {
    setRunning((prev) => {
      const next = new Set(prev);
      for (const id of ids) {
        if (value) next.add(id);
        else next.delete(id);
      }
      onActiveAgentsChange(next);
      // The real signal for "is a request actually in flight right now"
      // — every delegate() call (the first automatic one or a follow-up
      // chip) passes through here, so this reflects genuine execution
      // state, not a simulated timer.
      onExecutingChange(next.size > 0);
      return next;
    });
  }

  async function runAgent(agent: AgentRecord, task: string) {
    markRunning([agent.agent_id], true);
    try {
      const result = await api.delegate(agent.agent_id, task);
      setLog((l) => [
        ...l,
        {
          role: "result",
          agentId: agent.agent_id,
          text: result.content
            ? `${agent.name} (${agent.division}, via ${result.backend_name}): ${result.content}`
            : `${agent.name}: execution ${result.execution_id} ${result.status}.`,
        },
      ]);
    } catch (err) {
      setLog((l) => [
        ...l,
        { role: "error", text: `${agent.name} failed: ${err instanceof ApiError ? err.message : "could not reach the API"}` },
      ]);
    } finally {
      markRunning([agent.agent_id], false);
    }
  }

  async function handleSubmit(query: string) {
    if (!query.trim() || busy) return;
    setLog((l) => [...l, { role: "user", text: query }]);
    setValue("");
    setBusy(true);

    const zoneId = zoneIdForQuery(query);
    if (zoneId) scrollToZone(zoneId);
    else scrollToZone("agent-fabric");

    try {
      const matches = await api.agentFabricSearch(query);
      if (matches.length === 0) {
        onMatchedAgentsChange(new Set());
        setLog((l) => [...l, { role: "axiom", text: "No agents matched that in the real registry — try different wording." }]);
        return;
      }

      onMatchedAgentsChange(new Set(matches.map((a) => a.agent_id)));

      const [lead, ...rest] = matches;
      setLog((l) => [
        ...l,
        {
          role: "axiom",
          text: `Running this on ${lead.name} (${lead.division}) — the closest real match.${
            rest.length ? ` ${rest.length} more matched; run any of them on the same task too:` : ""
          }`,
          agents: rest,
          task: query,
        },
      ]);
      await runAgent(lead, query);
    } catch (err) {
      onMatchedAgentsChange(new Set());
      setLog((l) => [...l, { role: "error", text: err instanceof ApiError ? err.message : "Could not reach the Axiom API." }]);
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
                <span className="talkback-role">
                  {entry.role === "user" ? "you" : entry.role === "error" ? "!" : entry.role === "result" ? "ran" : "axiom"}
                </span>
                <div className="talkback-text">
                  {entry.text}
                  {"agents" in entry && entry.agents && entry.agents.length > 0 && (
                    <div className="talkback-agents">
                      {entry.agents.map((agent) => (
                        <button
                          key={agent.agent_id}
                          className="talkback-agent-chip"
                          disabled={busy || running.has(agent.agent_id)}
                          onClick={() => entry.task && runAgent(agent, entry.task)}
                          title={agent.description}
                        >
                          {running.has(agent.agent_id) ? "running…" : agent.name}{" "}
                          <span className="talkback-agent-division">{agent.division}</span>
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
              placeholder="Tell Axiom what you need done…"
              disabled={busy}
              aria-label="Command Axiom"
            />
            <button type="submit" disabled={busy || !value.trim()}>
              {busy ? "…" : "Run"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

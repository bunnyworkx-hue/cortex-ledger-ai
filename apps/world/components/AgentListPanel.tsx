"use client";

import { useMemo, useState } from "react";
import { divisionColorMap } from "@/lib/layout";
import { useOpenByDefault } from "@/lib/useOpenByDefault";
import type { AgentRecord } from "@/lib/api";

// The Agent Fabric point cloud now spins continuously (never holds
// still), so hovering one specific real agent by aiming at a moving
// point got harder. This is the same real roster, same real hover/click
// contract (onHoverAgent/onSelectAgent — the exact callbacks
// AgentFabricZone's own instanced points use), just laid out as a still
// list a human can actually read and click without chasing the cluster.
export function AgentListPanel({
  agents,
  activeAgentIds,
  matchedAgentIds,
  hoveredAgentId,
  onHoverAgent,
  onSelectAgent,
}: {
  agents: AgentRecord[];
  activeAgentIds: Set<string>;
  matchedAgentIds: Set<string>;
  hoveredAgentId: string | null;
  onHoverAgent: (id: string | null) => void;
  onSelectAgent: (agent: AgentRecord) => void;
}) {
  const [open, setOpen] = useOpenByDefault();
  const [filter, setFilter] = useState("");

  const divisionColor = useMemo(() => divisionColorMap(agents), [agents]);
  const searching = matchedAgentIds.size > 0;

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return agents;
    return agents.filter(
      (a) => a.name.toLowerCase().includes(q) || a.division.toLowerCase().includes(q) || a.category.toLowerCase().includes(q)
    );
  }, [agents, filter]);

  return (
    <div className="agent-list">
      <button className="agent-list-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        Agent Roster {agents.length ? `(${agents.length})` : ""}
      </button>

      {open && (
        <div className="agent-list-panel">
          <input
            className="agent-list-filter"
            placeholder="filter by name, division, category…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          {!agents.length && <div className="agent-list-loading">loading live registry…</div>}
          <div className="agent-list-rows">
            {filtered.map((agent) => {
              const active = activeAgentIds.has(agent.agent_id);
              const hovered = hoveredAgentId === agent.agent_id;
              const matched = matchedAgentIds.has(agent.agent_id);
              const dimmed = searching && !matched && !active && !hovered;
              return (
                <button
                  key={agent.agent_id}
                  className={`agent-list-row${active ? " agent-list-row-active" : ""}${hovered ? " agent-list-row-hovered" : ""}${dimmed ? " agent-list-row-dim" : ""}`}
                  onMouseEnter={() => onHoverAgent(agent.agent_id)}
                  onMouseLeave={() => onHoverAgent(null)}
                  onClick={() => onSelectAgent(agent)}
                >
                  <span className="agent-list-dot" style={{ background: divisionColor.get(agent.division) ?? "#8f97ea" }} />
                  <span className="agent-list-name">{agent.name}</span>
                  <span className="agent-list-division">{agent.division}</span>
                </button>
              );
            })}
            {agents.length > 0 && !filtered.length && <div className="agent-list-empty">no agents match &ldquo;{filter}&rdquo;</div>}
          </div>
        </div>
      )}
    </div>
  );
}

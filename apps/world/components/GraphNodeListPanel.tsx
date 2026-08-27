"use client";

import { useMemo, useState } from "react";
import { useOpenByDefault } from "@/lib/useOpenByDefault";
import type { GraphNode } from "@/lib/graphData.server";

// Same fix as AgentListPanel, for the other cluster that now spins
// continuously: the Knowledge Fabric graph. Real nodes, same real
// hover/click contract GraphifyZone's own instanced points use — just a
// still list a human can actually aim at.
export function GraphNodeListPanel({
  nodes,
  available,
  hoveredNodeId,
  onHoverNode,
  onSelectNode,
}: {
  nodes: GraphNode[];
  available: boolean;
  hoveredNodeId: string | null;
  onHoverNode: (id: string | null) => void;
  onSelectNode: (node: GraphNode) => void;
}) {
  const [open, setOpen] = useOpenByDefault();
  const [filter, setFilter] = useState("");

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return nodes;
    return nodes.filter((n) => n.label.toLowerCase().includes(q) || n.file_type.toLowerCase().includes(q));
  }, [nodes, filter]);

  if (!available) return null;

  return (
    <div className="graph-list">
      <button className="graph-list-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        Knowledge Nodes {nodes.length ? `(${nodes.length})` : ""}
      </button>

      {open && (
        <div className="graph-list-panel">
          <input
            className="graph-list-filter"
            placeholder="filter by label, file type…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div className="graph-list-rows">
            {filtered.map((node) => {
              const hovered = hoveredNodeId === node.id;
              return (
                <button
                  key={node.id}
                  className={`graph-list-row${hovered ? " graph-list-row-hovered" : ""}`}
                  onMouseEnter={() => onHoverNode(node.id)}
                  onMouseLeave={() => onHoverNode(null)}
                  onClick={() => onSelectNode(node)}
                >
                  <span className="graph-list-name">{node.label}</span>
                  <span className="graph-list-meta">
                    c{node.community} · deg {node.degree}
                  </span>
                </button>
              );
            })}
            {nodes.length > 0 && !filtered.length && <div className="graph-list-empty">no nodes match &ldquo;{filter}&rdquo;</div>}
          </div>
        </div>
      )}
    </div>
  );
}

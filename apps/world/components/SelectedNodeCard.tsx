"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { GraphNode } from "@/lib/graphData.server";

// Same real-interactivity pattern as SelectedAgentCard, applied to the
// Knowledge Fabric zone: real fields from the real sampled graph node,
// plus a real live call to the actual Graphify MCP tool
// (get_neighbors) rather than just static data already shipped to the
// client — a genuine graph traversal, not a canned response.
export function SelectedNodeCard({ node, onClose }: { node: GraphNode; onClose: () => void }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ text: string; isError: boolean } | null>(null);

  async function findNeighbors() {
    setBusy(true);
    setResult(null);
    try {
      const response = await api.callTool("get_neighbors", { label: node.label });
      if ("approval_id" in response) {
        setResult({ text: "Unexpectedly requires approval — get_neighbors should be low-risk.", isError: true });
      } else {
        const text = typeof response.content?.text === "string" ? response.content.text : JSON.stringify(response.content);
        setResult({ text: text.slice(0, 500), isError: response.is_error });
      }
    } catch (err) {
      setResult({ text: err instanceof ApiError ? err.message : "Could not reach the Cortex Ledger AI API", isError: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="selected-node">
      <div className="selected-node-head">
        <div>
          <div className="selected-node-name">{node.label}</div>
          <div className="selected-node-meta">
            {node.file_type} · community {node.community} · degree {node.degree}
          </div>
        </div>
        <button className="selected-node-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      {node.source_file && (
        <div className="selected-node-source">
          {node.source_file}
          {node.source_location ? `:${node.source_location}` : ""}
        </div>
      )}

      <button className="selected-node-run" onClick={findNeighbors} disabled={busy}>
        {busy ? "Querying live graph…" : "Find real neighbors (live Graphify call)"}
      </button>
      {result && <div className={`selected-node-result ${result.isError ? "selected-node-result-error" : ""}`}>{result.text}</div>}
    </div>
  );
}

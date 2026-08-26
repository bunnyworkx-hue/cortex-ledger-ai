"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ToolDefinition } from "@/lib/api";

// §18's MCP Interoperability Layer — real, not the same content as Tool
// Registry (which shows what each tool does) or Policy Engine (which
// shows the risk rule). This is specifically about the protocol layer:
// which external systems are connected via MCP, and how many real tools
// each one actually contributed on discovery — derived from the same
// GET /v1/tools every other panel already fetches, by reading each
// tool's real `source` field (e.g. "mcp:graphify"), not a new endpoint.
export function McpAreaPanel() {
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

  const servers = new Map<string, number>();
  let nativeCount = 0;
  for (const tool of tools ?? []) {
    if (tool.source.startsWith("mcp:")) {
      const server = tool.source.slice("mcp:".length);
      servers.set(server, (servers.get(server) ?? 0) + 1);
    } else {
      nativeCount += 1;
    }
  }

  return (
    <div className="mcp-area">
      <button className="mcp-area-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        MCP Layer {servers.size > 0 ? `(${servers.size})` : ""}
      </button>

      {open && (
        <div className="mcp-area-panel">
          <div className="mcp-area-head">
            Axiom → MCP → external servers. Real connected servers and how
            many real tools each contributed on discovery.
          </div>
          {error && <div className="mcp-area-error">{error}</div>}
          {!tools && !error && <div className="mcp-area-loading">loading live registry…</div>}

          {tools && (
            <>
              <div className="mcp-diagram">
                <div className="mcp-node mcp-node-axiom">AXIOM</div>
                <div className="mcp-arrow">↓</div>
                <div className="mcp-node mcp-node-mcp">MCP</div>
                <div className="mcp-branches">
                  {[...servers.entries()].map(([server, count]) => (
                    <div key={server} className="mcp-branch">
                      <div className="mcp-branch-line" />
                      <div className="mcp-node mcp-node-server">
                        {server}
                        <span className="mcp-node-count">{count} tools</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {servers.size === 0 && (
                <div className="mcp-area-empty">No MCP server reachable right now — start one via `./scripts/dev/graphify-serve.sh`.</div>
              )}
              <div className="mcp-area-native">
                {nativeCount} native tool{nativeCount === 1 ? "" : "s"} bypass MCP entirely (built directly into Axiom).
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

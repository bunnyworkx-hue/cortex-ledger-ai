"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ToolDefinition } from "@/lib/api";

type ArgValues = Record<string, string>;
type ToolResult = { text: string; isError: boolean; pending: boolean };

// A genuinely generic, schema-driven caller — every one of the real 12
// tools GET /v1/tools returns works here, including ones added after
// this was written, because the input fields are built from each real
// tool's own input_schema.required/properties rather than hand-coded
// per tool name.
export function ToolRegistryPanel() {
  const [open, setOpen] = useState(false);
  const [tools, setTools] = useState<ToolDefinition[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [argValues, setArgValues] = useState<Record<string, ArgValues>>({});
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const [results, setResults] = useState<Record<string, ToolResult>>({});

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

  function setArg(toolName: string, argName: string, value: string) {
    setArgValues((prev) => ({ ...prev, [toolName]: { ...prev[toolName], [argName]: value } }));
  }

  async function call(tool: ToolDefinition) {
    const required = tool.input_schema.required ?? [];
    const values = argValues[tool.name] ?? {};

    // Real bug this caught, live: an empty numeric field silently became
    // Number("") === 0 (a genuinely valid-looking call graphify accepted
    // for community_id), and an empty required string reached
    // get_neighbors and crashed Graphify's own handler with a raw Python
    // "not enough values to unpack" exception instead of a clean
    // validation error. Neither is a bug this panel can fix upstream —
    // but it shouldn't let an unfilled required field reach the API at
    // all, so it can't happen here regardless of what the tool does with
    // bad input.
    const missing = required.filter((key) => !(values[key] ?? "").trim());
    if (missing.length > 0) {
      setResults((prev) => ({
        ...prev,
        [tool.name]: { text: `Fill in: ${missing.join(", ")}`, isError: true, pending: false },
      }));
      return;
    }
    const invalidNumeric = required.filter((key) => {
      const propType = tool.input_schema.properties?.[key]?.type;
      return (propType === "integer" || propType === "number") && Number.isNaN(Number(values[key]));
    });
    if (invalidNumeric.length > 0) {
      setResults((prev) => ({
        ...prev,
        [tool.name]: { text: `${invalidNumeric.join(", ")} must be a number`, isError: true, pending: false },
      }));
      return;
    }

    setBusy((prev) => new Set(prev).add(tool.name));
    setResults((prev) => {
      const next = { ...prev };
      delete next[tool.name];
      return next;
    });
    try {
      const args: Record<string, unknown> = {};
      for (const key of required) {
        const raw = values[key];
        const propType = tool.input_schema.properties?.[key]?.type;
        args[key] = propType === "integer" || propType === "number" ? Number(raw) : raw;
      }

      const result = await api.callTool(tool.name, args);
      if ("approval_id" in result) {
        setResults((prev) => ({
          ...prev,
          [tool.name]: { text: "High risk — sent to Human Approval (see panel, top right).", isError: false, pending: true },
        }));
      } else {
        setResults((prev) => ({
          ...prev,
          [tool.name]: { text: JSON.stringify(result.content).slice(0, 400), isError: result.is_error, pending: false },
        }));
      }
    } catch (err) {
      setResults((prev) => ({
        ...prev,
        [tool.name]: { text: err instanceof ApiError ? err.message : "Could not reach the Axiom API", isError: true, pending: false },
      }));
    } finally {
      setBusy((prev) => {
        const next = new Set(prev);
        next.delete(tool.name);
        return next;
      });
    }
  }

  return (
    <div className="tool-registry">
      <button className="tool-registry-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        Tool Registry {tools ? `(${tools.length})` : ""}
      </button>

      {open && (
        <div className="tool-registry-panel">
          <div className="tool-registry-head">
            Every real registered tool — required fields call it with real arguments.
          </div>
          {error && <div className="tool-registry-error">{error}</div>}
          {!tools && !error && <div className="tool-registry-loading">loading live registry…</div>}

          {tools?.map((tool) => {
            const required = tool.input_schema.required ?? [];
            const result = results[tool.name];
            return (
              <div key={tool.name} className="tool-card">
                <div className="tool-card-head">
                  <span className="tool-name">{tool.name}</span>
                  <span className={`tool-source tool-source-${tool.source.startsWith("mcp") ? "mcp" : "native"}`}>
                    {tool.source}
                  </span>
                  <span className={`tool-risk tool-risk-${tool.risk_level}`}>{tool.risk_level}</span>
                </div>
                <div className="tool-description">{tool.description}</div>

                {required.length > 0 && (
                  <div className="tool-args">
                    {required.map((key) => {
                      const propType = tool.input_schema.properties?.[key]?.type;
                      const isNumeric = propType === "integer" || propType === "number";
                      return (
                        <input
                          key={key}
                          type={isNumeric ? "number" : "text"}
                          placeholder={key}
                          value={argValues[tool.name]?.[key] ?? ""}
                          onChange={(e) => setArg(tool.name, key, e.target.value)}
                        />
                      );
                    })}
                  </div>
                )}

                <div className="tool-card-foot">
                  <button onClick={() => call(tool)} disabled={busy.has(tool.name)}>
                    {busy.has(tool.name) ? "calling…" : "Call"}
                  </button>
                  {result && (
                    <span className={`tool-result ${result.isError ? "tool-result-error" : result.pending ? "tool-result-pending" : ""}`}>
                      {result.text}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

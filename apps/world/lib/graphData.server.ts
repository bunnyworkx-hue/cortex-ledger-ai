import "server-only";
import { readFile } from "fs/promises";
import path from "path";

// Real Graphify extraction output (var/graphify-out/graph.json, gitignored
// — see docs/graphify/GRAPHIFY_AUDIT.md for how it's produced), read
// directly server-side rather than round-tripping through the MCP tools:
// those return LLM-formatted text, not bulk structured JSON (a real,
// documented finding — see axiom_core.knowledge.types.KnowledgeAnswer's
// docstring), so they're the wrong shape for rendering 1,121 real graph
// nodes as 3D geometry. The raw graph.json is the same real artifact
// /v1/knowledge/* queries against, just read directly instead of through
// one text-formatted MCP call per node.

export type GraphNode = {
  id: string;
  label: string;
  community: number;
  file_type: string;
};

export type GraphLink = {
  source: string;
  target: string;
  relation: string;
  confidence: "EXTRACTED" | "INFERRED" | "AMBIGUOUS" | string;
};

export type GraphSnapshot = {
  available: boolean;
  nodeCount: number;
  linkCount: number;
  communityCount: number;
  nodes: GraphNode[];
  links: GraphLink[];
};

const GRAPH_PATH = path.join(process.cwd(), "..", "..", "var", "graphify-out", "graph.json");

// The full real graph is 1,121 nodes / 1,594 edges — fine to ship once,
// but the highest-degree nodes per community are what actually reads as
// "the graph" visually, so this samples down to a real, representative
// subset rather than rendering all of it as an undifferentiated point
// cloud. Every node/edge kept is real data from the actual extraction,
// not synthesized.
const MAX_NODES = 400;

export async function loadGraphSnapshot(): Promise<GraphSnapshot> {
  let raw: string;
  try {
    raw = await readFile(GRAPH_PATH, "utf-8");
  } catch {
    return { available: false, nodeCount: 0, linkCount: 0, communityCount: 0, nodes: [], links: [] };
  }

  const parsed = JSON.parse(raw) as {
    nodes: Array<{ id: string; label?: string; community?: number; file_type?: string }>;
    links: Array<{ source: string; target: string; relation?: string; confidence?: string }>;
  };

  const degree = new Map<string, number>();
  for (const link of parsed.links) {
    degree.set(link.source, (degree.get(link.source) ?? 0) + 1);
    degree.set(link.target, (degree.get(link.target) ?? 0) + 1);
  }

  const allNodes: GraphNode[] = parsed.nodes.map((n) => ({
    id: n.id,
    label: n.label ?? n.id,
    community: n.community ?? 0,
    file_type: n.file_type ?? "unknown",
  }));

  const sorted = [...allNodes].sort((a, b) => (degree.get(b.id) ?? 0) - (degree.get(a.id) ?? 0));
  const kept = sorted.slice(0, MAX_NODES);
  const keptIds = new Set(kept.map((n) => n.id));

  const links: GraphLink[] = parsed.links
    .filter((l) => keptIds.has(l.source) && keptIds.has(l.target))
    .map((l) => ({
      source: l.source,
      target: l.target,
      relation: l.relation ?? "related_to",
      confidence: l.confidence ?? "EXTRACTED",
    }));

  const communityCount = new Set(allNodes.map((n) => n.community)).size;

  return {
    available: true,
    nodeCount: allNodes.length,
    linkCount: parsed.links.length,
    communityCount,
    nodes: kept,
    links,
  };
}

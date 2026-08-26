import { loadGraphSnapshot } from "@/lib/graphData.server";
import { World } from "@/components/World";

// A server component so the real Graphify extraction file
// (var/graphify-out/graph.json) can be read directly, once, before the
// client 3D scene mounts — see lib/graphData.server.ts for why this
// reads the file instead of the MCP tools (they return LLM-formatted
// text, not bulk structured JSON).
//
// Forced dynamic: reading a local file with no fetch()/dynamic API in it
// would otherwise let Next statically prerender this page at build time
// and freeze whatever graph.json looked like then — wrong for data that
// changes every time someone re-runs `graphify extract`.
export const dynamic = "force-dynamic";

export default async function Page() {
  const graph = await loadGraphSnapshot();
  return <World graph={graph} />;
}

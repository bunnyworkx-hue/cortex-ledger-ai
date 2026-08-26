import { ZONES } from "@/lib/zones";

// A minimal escape hatch: the Talk-Back command bar lives outside the
// R3F <Canvas> (plain HTML, fixed to the viewport) so it stays visible
// regardless of scroll, but it still needs to drive scroll position —
// drei's useScroll() only works inside the Canvas tree. A tiny component
// mounted inside <ScrollControls> (see World.tsx) publishes the real
// scroll container element here once; Talk-Back reads it to scroll
// programmatically when a command names a zone.
export const scrollBridge: { el: HTMLElement | null } = { el: null };

const ZONE_KEYWORDS: Record<string, string[]> = {
  "agent-fabric": ["agent", "agents", "workforce", "finance", "marketing", "sales", "engineering", "division"],
  graphify: ["graph", "graphify", "knowledge", "codebase", "architecture", "authentication"],
  execution: ["hermes", "execution", "model", "claude", "backend", "run", "execute"],
  entry: ["entry", "start", "home", "beginning"],
};

export function zoneIdForQuery(query: string): string | null {
  const q = query.toLowerCase();
  for (const [zoneId, keywords] of Object.entries(ZONE_KEYWORDS)) {
    if (keywords.some((k) => q.includes(k))) return zoneId;
  }
  return null;
}

export function scrollToZone(zoneId: string): boolean {
  const el = scrollBridge.el;
  const zone = ZONES.find((z) => z.id === zoneId);
  if (!el || !zone) return false;
  const target = zone.start * (el.scrollHeight - el.clientHeight);
  el.scrollTo({ top: target, behavior: "smooth" });
  return true;
}

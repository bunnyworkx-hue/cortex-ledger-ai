// Deterministic pseudo-random positioning — seeded by a string/index, not
// Math.random(), so every render (and server/client hydration) places
// the same real agent or graph node in the same spot instead of
// reshuffling every reload.

function seededRandom(seed: string): () => number {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  };
}

/**
 * Places agents in angular sectors by division — one sector per real
 * division, sized proportionally to that division's real agent count, so
 * the biggest real divisions (engineering, specialized) visibly occupy
 * the most space rather than every division getting equal real estate
 * regardless of size.
 */
export function agentClusterPositions(
  divisionCounts: Record<string, number>,
  radius = 3.4
): Map<string, [number, number, number][]> {
  const divisions = Object.entries(divisionCounts).sort((a, b) => b[1] - a[1]);
  const total = divisions.reduce((sum, [, n]) => sum + n, 0) || 1;

  const result = new Map<string, [number, number, number][]>();
  let angleCursor = 0;
  for (const [division, count] of divisions) {
    const sectorSpan = (count / total) * Math.PI * 2;
    const rand = seededRandom(division);
    const positions: [number, number, number][] = [];
    for (let i = 0; i < count; i++) {
      const angle = angleCursor + rand() * sectorSpan;
      const r = radius * (0.35 + 0.65 * rand());
      const y = (rand() - 0.5) * 1.6;
      positions.push([Math.cos(angle) * r, y, Math.sin(angle) * r]);
    }
    result.set(division, positions);
    angleCursor += sectorSpan;
  }
  return result;
}

/**
 * Places graph nodes by real community id: each community gets its own
 * cluster center arranged in a ring, with member nodes jittered around
 * it — a real, if simplified, stand-in for a force-directed layout that
 * still reflects genuine community structure from the extraction.
 */
export function graphNodePositions(
  nodes: { id: string; community: number }[],
  radius = 3.2
): Map<string, [number, number, number]> {
  const communities = [...new Set(nodes.map((n) => n.community))].sort((a, b) => a - b);
  const clusterCenters = new Map<number, [number, number, number]>();
  communities.forEach((c, i) => {
    const angle = (i / communities.length) * Math.PI * 2;
    const clusterRadius = radius * 0.75;
    clusterCenters.set(c, [Math.cos(angle) * clusterRadius, 0, Math.sin(angle) * clusterRadius]);
  });

  const positions = new Map<string, [number, number, number]>();
  for (const node of nodes) {
    const [cx, cy, cz] = clusterCenters.get(node.community) ?? [0, 0, 0];
    const rand = seededRandom(node.id);
    const jitter = 0.9;
    positions.set(node.id, [
      cx + (rand() - 0.5) * jitter * 2,
      cy + (rand() - 0.5) * jitter,
      cz + (rand() - 0.5) * jitter * 2,
    ]);
  }
  return positions;
}

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
 * Places each real agent (by its real agent_id) in an angular sector by
 * division — one sector per real division, sized proportionally to that
 * division's real agent count, so the biggest real divisions
 * (engineering, specialized) visibly occupy the most space. Seeded by
 * agent_id rather than by division+index, so a given real agent always
 * lands in the same spot regardless of list order — a stable identity a
 * caller can look up later to highlight one specific agent.
 */
export function agentPositions(
  agents: { agent_id: string; division: string }[],
  radius = 3.4
): Map<string, [number, number, number]> {
  const byDivision = new Map<string, string[]>();
  for (const agent of agents) {
    const list = byDivision.get(agent.division) ?? [];
    list.push(agent.agent_id);
    byDivision.set(agent.division, list);
  }
  const divisions = [...byDivision.entries()].sort((a, b) => b[1].length - a[1].length);
  const total = agents.length || 1;

  const positions = new Map<string, [number, number, number]>();
  let angleCursor = 0;
  for (const [, agentIds] of divisions) {
    const sectorSpan = (agentIds.length / total) * Math.PI * 2;
    for (const agentId of agentIds) {
      const rand = seededRandom(agentId);
      const angle = angleCursor + rand() * sectorSpan;
      const r = radius * (0.35 + 0.65 * rand());
      const y = (rand() - 0.5) * 1.6;
      positions.set(agentId, [Math.cos(angle) * r, y, Math.sin(angle) * r]);
    }
    angleCursor += sectorSpan;
  }
  return positions;
}

// Same restrained, division-distinct palette used everywhere a division
// needs a color — the 3D point cloud and the side roster list both call
// divisionColorMap so a division always reads as the same color in both
// places, rather than two independent color assignments drifting apart.
export const DIVISION_COLOR = [
  "#7C86EA", "#6FC7C2", "#E0A860", "#D287A6", "#8FBF6E", "#8DA3D6",
  "#C98F6B", "#6FB0D8", "#B491DD", "#8FC79A", "#D6A5D0", "#7FA8B8",
];

export function divisionColorMap(agents: { division: string }[]): Map<string, string> {
  const counts = new Map<string, number>();
  for (const agent of agents) counts.set(agent.division, (counts.get(agent.division) ?? 0) + 1);
  const divisions = [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => d);
  const map = new Map<string, string>();
  divisions.forEach((d, i) => map.set(d, DIVISION_COLOR[i % DIVISION_COLOR.length]));
  return map;
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

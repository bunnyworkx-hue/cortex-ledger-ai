"use client";

import { Instance, Instances, Text } from "@react-three/drei";
import { useMemo } from "react";
import { agentPositions } from "@/lib/layout";
import { ZONES } from "@/lib/zones";
import type { AgentRecord } from "@/lib/api";

const CENTER = ZONES[1].center;

// A restrained, division-distinct palette (not a rainbow) — enough hue
// separation to read as "different divisions" without turning the
// cluster into noise.
const DIVISION_COLOR = [
  "#7C86EA", "#6FC7C2", "#E0A860", "#D287A6", "#8FBF6E", "#8DA3D6",
  "#C98F6B", "#6FB0D8", "#B491DD", "#8FC79A", "#D6A5D0", "#7FA8B8",
];

const ACTIVE_COLOR = "#F5C24B";
const DIM_COLOR = "#33364a";

export function AgentFabricZone({
  agents,
  activeAgentIds,
  matchedAgentIds,
}: {
  agents: AgentRecord[];
  activeAgentIds: Set<string>;
  matchedAgentIds: Set<string>;
}) {
  const divisions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const agent of agents) counts.set(agent.division, (counts.get(agent.division) ?? 0) + 1);
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => d);
  }, [agents]);
  const divisionColor = useMemo(() => {
    const map = new Map<string, string>();
    divisions.forEach((d, i) => map.set(d, DIVISION_COLOR[i % DIVISION_COLOR.length]));
    return map;
  }, [divisions]);
  const positions = useMemo(() => agentPositions(agents), [agents]);

  const divisionCenters = useMemo(() => {
    const sums = new Map<string, { x: number; z: number; n: number }>();
    for (const agent of agents) {
      const pos = positions.get(agent.agent_id);
      if (!pos) continue;
      const acc = sums.get(agent.division) ?? { x: 0, z: 0, n: 0 };
      acc.x += pos[0];
      acc.z += pos[2];
      acc.n += 1;
      sums.set(agent.division, acc);
    }
    return sums;
  }, [agents, positions]);

  return (
    <group position={CENTER}>
      <Text position={[0, 3, 0]} fontSize={0.34} color="#eef0fb" anchorX="center" letterSpacing={0.03}>
        AGENT FABRIC
      </Text>
      <Text position={[0, 2.5, 0]} fontSize={0.13} color="#8f95bd" anchorX="center">
        {agents.length ? `${agents.length} real agents · ${divisions.length} divisions` : "loading live registry…"}
      </Text>

      <Instances limit={Math.max(agents.length, 1)}>
        <sphereGeometry args={[0.032, 8, 8]} />
        <meshStandardMaterial roughness={0.4} />
        {agents.map((agent) => {
          const active = activeAgentIds.has(agent.agent_id);
          const searching = matchedAgentIds.size > 0;
          const matched = matchedAgentIds.has(agent.agent_id);
          const baseColor = divisionColor.get(agent.division) ?? "#8f97ea";

          // Idle (no search yet): everyone at full color/scale. Once a
          // search has real results, non-matches fade back — the "the
          // irrelevant agents fade back, selected agents become
          // highlighted" behavior from the original spec's Agent
          // Discovery section, tied to a real search result set rather
          // than simulated.
          let color = baseColor;
          let scale = 1;
          if (active) {
            color = ACTIVE_COLOR;
            scale = 2.6;
          } else if (searching) {
            color = matched ? baseColor : DIM_COLOR;
            scale = matched ? 1.35 : 0.55;
          }

          return (
            <Instance key={agent.agent_id} position={positions.get(agent.agent_id) ?? [0, 0, 0]} color={color} scale={scale} />
          );
        })}
      </Instances>

      {divisions.slice(0, 8).map((division) => {
        const c = divisionCenters.get(division);
        if (!c) return null;
        const cx = c.x / c.n;
        const cz = c.z / c.n;
        const labelRadius = Math.hypot(cx, cz) + 0.55;
        const angle = Math.atan2(cz, cx);
        const count = agents.filter((a) => a.division === division).length;
        return (
          <Text
            key={division}
            position={[Math.cos(angle) * labelRadius, 0.9, Math.sin(angle) * labelRadius]}
            fontSize={0.1}
            color={divisionColor.get(division)}
            anchorX="center"
            letterSpacing={0.05}
          >
            {`${division.toUpperCase()} · ${count}`}
          </Text>
        );
      })}
    </group>
  );
}

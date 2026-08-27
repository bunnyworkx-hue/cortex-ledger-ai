"use client";

import { Instance, Instances, Text } from "@react-three/drei";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { ThreeEvent } from "@react-three/fiber";
import type { Dispatch, SetStateAction } from "react";
import type { Group } from "three";
import { agentPositions, divisionColorMap } from "@/lib/layout";
import { ZONES } from "@/lib/zones";
import type { AgentRecord } from "@/lib/api";

const CENTER = ZONES[1].center;

const ACTIVE_COLOR = "#F5C24B";
const HOVER_COLOR = "#FFFFFF";
const DIM_COLOR = "#33364a";

export function AgentFabricZone({
  agents,
  activeAgentIds,
  matchedAgentIds,
  hoveredAgentId,
  onHoverAgent,
  onSelectAgent,
}: {
  agents: AgentRecord[];
  activeAgentIds: Set<string>;
  matchedAgentIds: Set<string>;
  hoveredAgentId: string | null;
  onHoverAgent: Dispatch<SetStateAction<string | null>>;
  onSelectAgent: (agent: AgentRecord) => void;
}) {
  const hoveredId = hoveredAgentId;
  const cluster = useRef<Group>(null);
  useFrame((_, delta) => {
    if (cluster.current) cluster.current.rotation.y += delta * 0.06;
  });

  const divisions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const agent of agents) counts.set(agent.division, (counts.get(agent.division) ?? 0) + 1);
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => d);
  }, [agents]);
  const divisionColor = useMemo(() => divisionColorMap(agents), [agents]);
  const positions = useMemo(() => agentPositions(agents), [agents]);
  const byId = useMemo(() => new Map(agents.map((a) => [a.agent_id, a])), [agents]);

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

  const hoveredAgent = hoveredId ? byId.get(hoveredId) : null;

  return (
    <group position={CENTER}>
      <Text position={[0, 3, 0]} fontSize={0.34} color="#eef0fb" anchorX="center" letterSpacing={0.03}>
        AGENT FABRIC
      </Text>
      <Text position={[0, 2.5, 0]} fontSize={0.13} color="#8f95bd" anchorX="center">
        {agents.length
          ? hoveredAgent
            ? `${hoveredAgent.name} · ${hoveredAgent.division} — click to inspect & delegate`
            : `${agents.length} real agents · ${divisions.length} divisions — hover to inspect, click to run`
          : "loading live registry…"}
      </Text>

      <group ref={cluster}>
      <Instances limit={Math.max(agents.length, 1)}>
        <sphereGeometry args={[0.032, 8, 8]} />
        <meshStandardMaterial roughness={0.4} />
        {agents.map((agent) => {
          const active = activeAgentIds.has(agent.agent_id);
          const hovered = hoveredId === agent.agent_id;
          const searching = matchedAgentIds.size > 0;
          const matched = matchedAgentIds.has(agent.agent_id);
          const baseColor = divisionColor.get(agent.division) ?? "#8f97ea";

          // Idle (no search yet): everyone at full color/scale. Once a
          // search has real results, non-matches fade back — the "the
          // irrelevant agents fade back, selected agents become
          // highlighted" behavior from the original spec's Agent
          // Discovery section, tied to a real search result set rather
          // than simulated. Hover/active take precedence over both.
          let color = baseColor;
          let scale = 1;
          if (active) {
            color = ACTIVE_COLOR;
            scale = 2.6;
          } else if (hovered) {
            color = HOVER_COLOR;
            scale = 2.1;
          } else if (searching) {
            color = matched ? baseColor : DIM_COLOR;
            scale = matched ? 1.35 : 0.55;
          }

          return (
            <Instance
              key={agent.agent_id}
              position={positions.get(agent.agent_id) ?? [0, 0, 0]}
              color={color}
              scale={scale}
              onPointerOver={(e: ThreeEvent<PointerEvent>) => {
                e.stopPropagation();
                onHoverAgent(agent.agent_id);
                document.body.style.cursor = "pointer";
              }}
              onPointerOut={(e: ThreeEvent<PointerEvent>) => {
                e.stopPropagation();
                onHoverAgent((prev) => (prev === agent.agent_id ? null : prev));
                document.body.style.cursor = "auto";
              }}
              onClick={(e: ThreeEvent<MouseEvent>) => {
                e.stopPropagation();
                onSelectAgent(agent);
              }}
            />
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
    </group>
  );
}

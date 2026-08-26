"use client";

import { Instance, Instances, Text } from "@react-three/drei";
import { useMemo } from "react";
import { agentClusterPositions } from "@/lib/layout";
import { ZONES } from "@/lib/zones";

const CENTER = ZONES[1].center;

// A restrained, division-distinct palette (not a rainbow) — enough hue
// separation to read as "different divisions" without turning the
// cluster into noise.
const DIVISION_COLOR = [
  "#7C86EA", "#6FC7C2", "#E0A860", "#D287A6", "#8FBF6E", "#8DA3D6",
  "#C98F6B", "#6FB0D8", "#B491DD", "#8FC79A", "#D6A5D0", "#7FA8B8",
];

export function AgentFabricZone({ byDivision }: { byDivision: Record<string, number> }) {
  const divisions = useMemo(() => Object.keys(byDivision).sort((a, b) => byDivision[b] - byDivision[a]), [byDivision]);
  const clusters = useMemo(() => agentClusterPositions(byDivision), [byDivision]);
  const total = useMemo(() => Object.values(byDivision).reduce((a, b) => a + b, 0), [byDivision]);

  return (
    <group position={CENTER}>
      <Text position={[0, 3, 0]} fontSize={0.34} color="#eef0fb" anchorX="center" letterSpacing={0.03}>
        AGENT FABRIC
      </Text>
      <Text position={[0, 2.5, 0]} fontSize={0.13} color="#8f95bd" anchorX="center">
        {total ? `${total} real agents · ${divisions.length} divisions` : "loading live registry…"}
      </Text>

      <Instances limit={300}>
        <sphereGeometry args={[0.032, 8, 8]} />
        <meshStandardMaterial color="#8f97ea" emissive="#4a55c7" emissiveIntensity={0.6} roughness={0.4} />
        {divisions.map((division, di) =>
          (clusters.get(division) ?? []).map((pos, i) => (
            <Instance key={`${division}-${i}`} position={pos} color={DIVISION_COLOR[di % DIVISION_COLOR.length]} />
          ))
        )}
      </Instances>

      {divisions.slice(0, 8).map((division, di) => {
        const positions = clusters.get(division) ?? [];
        if (!positions.length) return null;
        const cx = positions.reduce((s, p) => s + p[0], 0) / positions.length;
        const cz = positions.reduce((s, p) => s + p[2], 0) / positions.length;
        const labelRadius = Math.hypot(cx, cz) + 0.55;
        const angle = Math.atan2(cz, cx);
        return (
          <Text
            key={division}
            position={[Math.cos(angle) * labelRadius, 0.9, Math.sin(angle) * labelRadius]}
            fontSize={0.1}
            color={DIVISION_COLOR[di % DIVISION_COLOR.length]}
            anchorX="center"
            letterSpacing={0.05}
          >
            {`${division.toUpperCase()} · ${byDivision[division]}`}
          </Text>
        );
      })}
    </group>
  );
}

"use client";

import { Text } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import type { Mesh } from "three";
import { ZONES } from "@/lib/zones";

const CENTER = ZONES[3].center;

type BackendGroup = { label: string; backends: Record<string, string>; color: string; radius: number };

export function ExecutionZone({
  modelBackends,
  agentBackends,
  knowledgeBackends,
}: {
  modelBackends: Record<string, string>;
  agentBackends: Record<string, string>;
  knowledgeBackends: Record<string, string>;
}) {
  const core = useRef<Mesh>(null);
  useFrame((_, delta) => {
    if (core.current) core.current.rotation.y += delta * 0.15;
  });

  const groups: BackendGroup[] = useMemo(
    () => [
      { label: "MODEL GATEWAY", backends: modelBackends, color: "#7C86EA", radius: 1.9 },
      { label: "AGENT BACKENDS", backends: agentBackends, color: "#E0A860", radius: 2.7 },
      { label: "KNOWLEDGE GATEWAY", backends: knowledgeBackends, color: "#6FC7C2", radius: 3.5 },
    ],
    [modelBackends, agentBackends, knowledgeBackends]
  );

  return (
    <group position={CENTER}>
      <Text position={[0, 3, 0]} fontSize={0.34} color="#eef0fb" anchorX="center" letterSpacing={0.03}>
        EXECUTION ENGINE
      </Text>
      <Text position={[0, 2.5, 0]} fontSize={0.13} color="#8f95bd" anchorX="center">
        real registered backends, read live from /v1/models, /v1/agents, /v1/knowledge
      </Text>

      <mesh ref={core}>
        <icosahedronGeometry args={[0.55, 1]} />
        <meshStandardMaterial color="#4a55c7" emissive="#4a55c7" emissiveIntensity={0.5} wireframe />
      </mesh>

      {groups.map((group) => {
        const entries = Object.entries(group.backends);
        return entries.map(([name, status], i) => {
          const angle = (i / Math.max(entries.length, 1)) * Math.PI * 2 + group.radius;
          const x = Math.cos(angle) * group.radius;
          const z = Math.sin(angle) * group.radius;
          const configured = status === "configured";
          // Hermes is a real, distinct external agent runtime
          // (packages/axiom-hermes, a subprocess CLI call — not part of
          // Axiom's own execution path). CLAUDE.md §8-9's own framing:
          // "Hermes should never visually appear to own the Axiom
          // environment. Axiom controls access." — the gate ring is that
          // boundary made visible, not decoration.
          const isHermes = name === "hermes";
          return (
            <group key={`${group.label}-${name}`} position={[x, 0, z]}>
              {isHermes && (
                <mesh rotation={[Math.PI / 2, 0, 0]}>
                  <torusGeometry args={[0.27, 0.008, 8, 48]} />
                  <meshBasicMaterial color="#E0A860" transparent opacity={configured ? 0.6 : 0.2} />
                </mesh>
              )}
              <mesh>
                <sphereGeometry args={[0.16, 16, 16]} />
                <meshStandardMaterial
                  color={group.color}
                  emissive={configured ? group.color : "#3a3d4d"}
                  emissiveIntensity={configured ? 0.55 : 0.15}
                  roughness={0.35}
                />
              </mesh>
              <Text position={[0, -0.32, 0]} fontSize={0.09} color={group.color} anchorX="center">
                {name}
              </Text>
              <Text position={[0, -0.46, 0]} fontSize={0.06} color={configured ? "#7fd6a0" : "#8a8f9e"} anchorX="center">
                {isHermes ? `${status} · external gateway` : status}
              </Text>
            </group>
          );
        });
      })}

      {groups.map((group, gi) => (
        <Text
          key={group.label}
          position={[-3.4, 2 - gi * 0.24, 0]}
          fontSize={0.08}
          color={group.color}
          anchorX="left"
          letterSpacing={0.04}
        >
          {group.label}
        </Text>
      ))}
    </group>
  );
}

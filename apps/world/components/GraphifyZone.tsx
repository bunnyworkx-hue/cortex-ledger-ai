"use client";

import { Instance, Instances, Text } from "@react-three/drei";
import { useMemo } from "react";
import { BufferAttribute, BufferGeometry, Color } from "three";
import { graphNodePositions } from "@/lib/layout";
import { ZONES } from "@/lib/zones";
import type { GraphSnapshot } from "@/lib/graphData.server";

const CENTER = ZONES[2].center;
const EXTRACTED = new Color("#6FC7C2");
const INFERRED = new Color("#B491DD");

export function GraphifyZone({ graph }: { graph: GraphSnapshot }) {
  const positions = useMemo(() => graphNodePositions(graph.nodes), [graph.nodes]);

  const edgeGeometry = useMemo(() => {
    const verts: number[] = [];
    const colors: number[] = [];
    for (const link of graph.links) {
      const a = positions.get(link.source);
      const b = positions.get(link.target);
      if (!a || !b) continue;
      verts.push(...a, ...b);
      const c = link.confidence === "INFERRED" ? INFERRED : EXTRACTED;
      colors.push(c.r, c.g, c.b, c.r, c.g, c.b);
    }
    const geo = new BufferGeometry();
    geo.setAttribute("position", new BufferAttribute(new Float32Array(verts), 3));
    geo.setAttribute("color", new BufferAttribute(new Float32Array(colors), 3));
    return geo;
  }, [graph.links, positions]);

  return (
    <group position={CENTER}>
      <Text position={[0, 3, 0]} fontSize={0.34} color="#eef0fb" anchorX="center" letterSpacing={0.03}>
        KNOWLEDGE FABRIC
      </Text>
      <Text position={[0, 2.5, 0]} fontSize={0.13} color="#8f95bd" anchorX="center">
        {graph.available
          ? `${graph.nodeCount.toLocaleString()} real nodes · ${graph.linkCount.toLocaleString()} edges · ${graph.communityCount} communities (Graphify)`
          : "Graphify extraction not found — run `graphify extract` (see GRAPHIFY_INTEGRATION.md)"}
      </Text>

      {graph.available && (
        <>
          <lineSegments geometry={edgeGeometry}>
            <lineBasicMaterial vertexColors transparent opacity={0.35} />
          </lineSegments>

          <Instances limit={graph.nodes.length}>
            <sphereGeometry args={[0.028, 8, 8]} />
            <meshStandardMaterial color="#9fd8d4" emissive="#0e5f5a" emissiveIntensity={0.5} roughness={0.4} />
            {graph.nodes.map((node) => (
              <Instance key={node.id} position={positions.get(node.id) ?? [0, 0, 0]} />
            ))}
          </Instances>

          <Text position={[-2.4, -2.9, 0]} fontSize={0.09} color={"#6FC7C2"} anchorX="left">
            ── EXTRACTED (from source)
          </Text>
          <Text position={[0.6, -2.9, 0]} fontSize={0.09} color={"#B491DD"} anchorX="left">
            ── INFERRED (resolved)
          </Text>
        </>
      )}
    </group>
  );
}

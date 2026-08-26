"use client";

import { Text } from "@react-three/drei";
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { Group } from "three";
import { ZONES } from "@/lib/zones";

const CENTER = ZONES[0].center;

export function EntryZone() {
  const ring = useRef<Group>(null);

  useFrame((_, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.05;
  });

  return (
    <group position={CENTER}>
      <group ref={ring}>
        {[3.2, 4.4, 5.6].map((r, i) => (
          <mesh key={r} rotation={[Math.PI / 2.4, 0, (i * Math.PI) / 6]}>
            <torusGeometry args={[r, 0.006, 8, 96]} />
            <meshBasicMaterial color="#5b67d8" transparent opacity={0.35} />
          </mesh>
        ))}
      </group>
      <Text
        position={[0, 0.9, 0]}
        fontSize={1.1}
        letterSpacing={0.04}
        color="#eef0fb"
        anchorX="center"
        anchorY="middle"
      >
        AXIOM OS
      </Text>
      <Text
        position={[0, -0.05, 0]}
        fontSize={0.16}
        letterSpacing={0.16}
        color="#9aa0c9"
        anchorX="center"
        anchorY="middle"
      >
        AUTONOMOUS EXECUTION — BUILT FOR BUSINESS OPERATIONS
      </Text>
      <Text
        position={[0, -0.75, 0]}
        fontSize={0.1}
        color="#5f6480"
        anchorX="center"
        anchorY="middle"
      >
        scroll to enter
      </Text>
    </group>
  );
}

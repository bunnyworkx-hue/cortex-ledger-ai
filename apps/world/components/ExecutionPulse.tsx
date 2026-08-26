"use client";

import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import { Vector3, type Mesh, type Group } from "three";
import { ZONES } from "@/lib/zones";

// A visible line from where a Talk-Back task gets routed — the Agent
// Fabric zone — to where it actually executes — the Execution Engine
// zone — with a pulse that travels it while a real delegate() call is
// in flight (driven by TalkBack's real `running` set via onExecutingChange,
// not a fake timer). This is the closest honest stand-in for the
// original spec's "watch the execution graph" (§20): it doesn't invent
// a multi-stage Planner/Verify trace the real backend doesn't report,
// but it does make the one real async hop — agent selected -> agent
// executing — visible and timed to when it's actually happening.
const START = new Vector3(...ZONES[1].center).setY(1.2);
const END = new Vector3(...ZONES[3].center).setY(1.2);

export function ExecutionPulse({ active }: { active: boolean }) {
  const pulse = useRef<Mesh>(null);
  const group = useRef<Group>(null);
  const t = useRef(0);

  useFrame((_, delta) => {
    if (!group.current || !pulse.current) return;
    if (active) {
      t.current = (t.current + delta * 0.35) % 1;
      const pos = START.clone().lerp(END, t.current);
      pulse.current.position.copy(pos);
      const scale = 1 + Math.sin(t.current * Math.PI) * 0.6;
      pulse.current.scale.setScalar(scale);
      group.current.visible = true;
    } else {
      group.current.visible = false;
      t.current = 0;
    }
  });

  const points = [START, END];

  return (
    <group ref={group} visible={false}>
      <line>
        <bufferGeometry onUpdate={(g) => g.setFromPoints(points)} />
        <lineBasicMaterial color="#F5C24B" transparent opacity={0.28} />
      </line>
      <mesh ref={pulse} position={START}>
        <sphereGeometry args={[0.12, 12, 12]} />
        <meshStandardMaterial color="#F5C24B" emissive="#F5C24B" emissiveIntensity={1.4} />
      </mesh>
    </group>
  );
}

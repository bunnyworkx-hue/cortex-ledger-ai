"use client";

import { Canvas } from "@react-three/fiber";
import { ScrollControls, Stars } from "@react-three/drei";
import { Suspense, useEffect, useState } from "react";
import { api, type AgentFabricStatus, type BackendStatus } from "@/lib/api";
import type { GraphSnapshot } from "@/lib/graphData.server";
import { CameraRig } from "./CameraRig";
import { ScrollBridgeSync } from "./ScrollBridgeSync";
import { ZoneOverlay } from "./ZoneOverlay";
import { EntryZone } from "./EntryZone";
import { AgentFabricZone } from "./AgentFabricZone";
import { GraphifyZone } from "./GraphifyZone";
import { ExecutionZone } from "./ExecutionZone";
import { TalkBack } from "./TalkBack";

const PAGES = 8;

export function World({ graph }: { graph: GraphSnapshot }) {
  const [fabric, setFabric] = useState<AgentFabricStatus | null>(null);
  const [models, setModels] = useState<BackendStatus | null>(null);
  const [agents, setAgents] = useState<BackendStatus | null>(null);
  const [knowledge, setKnowledge] = useState<BackendStatus | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.agentFabricStatus(), api.modelBackends(), api.agentBackends(), api.knowledgeBackends()])
      .then(([f, m, a, k]) => {
        if (cancelled) return;
        setFabric(f);
        setModels(m);
        setAgents(a);
        setKnowledge(k);
      })
      .catch((err) => {
        if (!cancelled) setLiveError(err instanceof Error ? err.message : "Failed to reach the Axiom API");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="world-root">
      {liveError && (
        <div className="world-error">
          Live system unreachable ({liveError}) — the Agent Fabric and Execution Engine zones need{" "}
          <code>./scripts/dev/run.sh</code> running at <code>http://127.0.0.1:8000</code>.
        </div>
      )}
      <Canvas camera={{ fov: 45, near: 0.1, far: 200 }} dpr={[1, 1.75]}>
        <color attach="background" args={["#0a0b12"]} />
        <fog attach="fog" args={["#0a0b12", 18, 46]} />
        <ambientLight intensity={0.5} />
        <pointLight position={[0, 8, 4]} intensity={40} color="#8791E8" />
        <Stars radius={80} depth={40} count={1800} factor={2.4} fade speed={0.3} />

        <ScrollControls pages={PAGES} damping={0.25}>
          <ScrollBridgeSync />
          <CameraRig />

          <Suspense fallback={null}>
            <EntryZone />
            <AgentFabricZone byDivision={fabric?.by_division ?? {}} />
            <GraphifyZone graph={graph} />
            <ExecutionZone
              modelBackends={models?.backends ?? {}}
              agentBackends={agents?.backends ?? {}}
              knowledgeBackends={knowledge?.backends ?? {}}
            />
          </Suspense>

          <ZoneOverlay pages={PAGES} />
        </ScrollControls>
      </Canvas>

      <TalkBack />
    </div>
  );
}

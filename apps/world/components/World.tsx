"use client";

import { Canvas } from "@react-three/fiber";
import { ScrollControls, Stars } from "@react-three/drei";
import { Suspense, useEffect, useState } from "react";
import { api, type AgentRecord, type BackendStatus } from "@/lib/api";
import type { GraphNode, GraphSnapshot } from "@/lib/graphData.server";
import { CameraRig } from "./CameraRig";
import { ScrollBridgeSync } from "./ScrollBridgeSync";
import { ZoneOverlay } from "./ZoneOverlay";
import { ZoneOverlaySync } from "./ZoneOverlaySync";
import { EntryZone } from "./EntryZone";
import { AgentFabricZone } from "./AgentFabricZone";
import { AgentListPanel } from "./AgentListPanel";
import { GraphifyZone } from "./GraphifyZone";
import { GraphNodeListPanel } from "./GraphNodeListPanel";
import { ExecutionZone, type SelectedBackend } from "./ExecutionZone";
import { SelectedBackendCard } from "./SelectedBackendCard";
import { ExecutionPulse } from "./ExecutionPulse";
import { TalkBack } from "./TalkBack";
import { ApprovalStation } from "./ApprovalStation";
import { ToolRegistryPanel } from "./ToolRegistryPanel";
import { PolicyEnginePanel } from "./PolicyEnginePanel";
import { McpAreaPanel } from "./McpAreaPanel";
import { SelectedAgentCard } from "./SelectedAgentCard";
import { SelectedNodeCard } from "./SelectedNodeCard";

const PAGES = 8;

export function World({ graph }: { graph: GraphSnapshot }) {
  const [roster, setRoster] = useState<AgentRecord[]>([]);
  const [models, setModels] = useState<BackendStatus | null>(null);
  const [agentBackends, setAgentBackends] = useState<BackendStatus | null>(null);
  const [knowledge, setKnowledge] = useState<BackendStatus | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const [activeAgentIds, setActiveAgentIds] = useState<Set<string>>(new Set());
  const [matchedAgentIds, setMatchedAgentIds] = useState<Set<string>>(new Set());
  const [hoveredAgentId, setHoveredAgentId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [executing, setExecuting] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentRecord | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedBackend, setSelectedBackend] = useState<SelectedBackend | null>(null);

  // One inspection target at a time — selecting a node while an agent
  // card is open (or vice versa) would otherwise render both in the
  // same right-center screen position simultaneously.
  function selectAgent(agent: AgentRecord | null) {
    setSelectedAgent(agent);
    if (agent) {
      setSelectedNode(null);
      setSelectedBackend(null);
    }
  }
  function selectNode(node: GraphNode | null) {
    setSelectedNode(node);
    if (node) {
      setSelectedAgent(null);
      setSelectedBackend(null);
    }
  }
  function selectBackend(backend: SelectedBackend | null) {
    setSelectedBackend(backend);
    if (backend) {
      setSelectedAgent(null);
      setSelectedNode(null);
    }
  }

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.listAgents(), api.modelBackends(), api.agentBackends(), api.knowledgeBackends()])
      .then(([r, m, a, k]) => {
        if (cancelled) return;
        setRoster(r);
        setModels(m);
        setAgentBackends(a);
        setKnowledge(k);
      })
      .catch((err) => {
        if (!cancelled) setLiveError(err instanceof Error ? err.message : "Failed to reach the Cortex Ledger AI API");
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
          <ZoneOverlaySync />

          <Suspense fallback={null}>
            <EntryZone />
            <AgentFabricZone
              agents={roster}
              activeAgentIds={activeAgentIds}
              matchedAgentIds={matchedAgentIds}
              hoveredAgentId={hoveredAgentId}
              onHoverAgent={setHoveredAgentId}
              onSelectAgent={selectAgent}
            />
            <GraphifyZone
              graph={graph}
              hoveredNodeId={hoveredNodeId}
              onHoverNode={setHoveredNodeId}
              onSelectNode={selectNode}
            />
            <ExecutionZone
              modelBackends={models?.backends ?? {}}
              agentBackends={agentBackends?.backends ?? {}}
              knowledgeBackends={knowledge?.backends ?? {}}
              onSelectBackend={selectBackend}
            />
            <ExecutionPulse active={executing} />
          </Suspense>
        </ScrollControls>
      </Canvas>

      <ZoneOverlay />
      <AgentListPanel
        agents={roster}
        activeAgentIds={activeAgentIds}
        matchedAgentIds={matchedAgentIds}
        hoveredAgentId={hoveredAgentId}
        onHoverAgent={setHoveredAgentId}
        onSelectAgent={selectAgent}
      />
      <GraphNodeListPanel
        nodes={graph.nodes}
        available={graph.available}
        hoveredNodeId={hoveredNodeId}
        onHoverNode={setHoveredNodeId}
        onSelectNode={selectNode}
      />
      <TalkBack
        onActiveAgentsChange={setActiveAgentIds}
        onMatchedAgentsChange={setMatchedAgentIds}
        onExecutingChange={setExecuting}
      />
      <ApprovalStation />
      <ToolRegistryPanel />
      <PolicyEnginePanel />
      <McpAreaPanel />
      {selectedAgent && <SelectedAgentCard agent={selectedAgent} onClose={() => setSelectedAgent(null)} />}
      {selectedNode && <SelectedNodeCard node={selectedNode} onClose={() => setSelectedNode(null)} />}
      {selectedBackend && <SelectedBackendCard backend={selectedBackend} onClose={() => setSelectedBackend(null)} />}
    </div>
  );
}

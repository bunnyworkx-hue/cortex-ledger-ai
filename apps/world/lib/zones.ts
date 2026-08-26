// Single source of truth for the scroll-driven journey: where each zone
// sits along the scroll timeline (0..1), where its 3D content is
// centered in world space, and where the camera goes to look at it.
// Both the camera rig and the HTML zone-label overlay read from this so
// neither can drift out of sync with the other.

export type Zone = {
  id: "entry" | "agent-fabric" | "graphify" | "execution";
  label: string;
  eyebrow: string;
  start: number;
  end: number;
  /** World-space center of this zone's 3D content. */
  center: [number, number, number];
  cameraPosition: [number, number, number];
  cameraTarget: [number, number, number];
};

// The journey moves the camera forward along -Z through four content
// clusters, each spaced far enough apart that scrolling reads as
// physically flying from one into the next — the "camera flies from
// outside into the interior" feel the spec asks for, built with a real
// camera transform instead of pre-rendered video.
const SPACING = 26;
const centerZ = (index: number) => -index * SPACING;

export const ZONES: Zone[] = [
  {
    id: "entry",
    label: "AXIOM OS",
    eyebrow: "AUTONOMOUS EXECUTION — BUILT FOR BUSINESS OPERATIONS",
    start: 0,
    end: 0.16,
    center: [0, 0, centerZ(0)],
    cameraPosition: [0, 1.6, centerZ(0) + 20],
    cameraTarget: [0, 0.5, centerZ(0)],
  },
  {
    id: "agent-fabric",
    label: "AGENT FABRIC",
    eyebrow: "254 real agents, 17 divisions — the workforce",
    start: 0.16,
    end: 0.42,
    center: [0, 0, centerZ(1)],
    cameraPosition: [0, 3.4, centerZ(1) + 9],
    cameraTarget: [0, 0.5, centerZ(1)],
  },
  {
    id: "graphify",
    label: "KNOWLEDGE FABRIC",
    eyebrow: "Graphify — what the system knows",
    start: 0.42,
    end: 0.68,
    center: [0, 0, centerZ(2)],
    cameraPosition: [0, 2.6, centerZ(2) + 8.5],
    cameraTarget: [0, 0, centerZ(2)],
  },
  {
    id: "execution",
    label: "EXECUTION ENGINE",
    eyebrow: "Model Gateway, Hermes, native backends — how work happens",
    start: 0.68,
    end: 0.94,
    center: [0, 0, centerZ(3)],
    cameraPosition: [0, 2.1, centerZ(3) + 7.5],
    cameraTarget: [0, 0.6, centerZ(3)],
  },
];

export function activeZone(scroll: number): Zone {
  for (const zone of ZONES) {
    if (scroll >= zone.start && scroll < zone.end) return zone;
  }
  return scroll < ZONES[0].start ? ZONES[0] : ZONES[ZONES.length - 1];
}

export function zoneProgress(scroll: number, zone: Zone): number {
  const span = zone.end - zone.start || 1;
  return Math.min(1, Math.max(0, (scroll - zone.start) / span));
}

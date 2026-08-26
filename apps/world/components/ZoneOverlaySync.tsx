"use client";

import { useScroll } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { ZONES, activeZone, zoneProgress } from "@/lib/zones";
import { zoneOverlayBridge } from "@/lib/zoneOverlayBridge";

// Mounted inside <ScrollControls>. Reads the real scroll offset every
// frame and imperatively fades the corresponding outside-the-Canvas
// label div in/out — no React state, no re-renders, no drei <Scroll
// html> (see zoneOverlayBridge.ts for why that broke).
export function ZoneOverlaySync() {
  const scroll = useScroll();

  useFrame(() => {
    const zone = activeZone(scroll.offset);
    const progress = zoneProgress(scroll.offset, zone);
    // Fade in over the first 15% of a zone's dwell, fade out over the
    // last 15% — reads as a crossfade between adjacent zone labels
    // instead of a hard cut.
    const eased = Math.min(1, progress / 0.15, (1 - progress) / 0.15);

    for (const z of ZONES) {
      const el = zoneOverlayBridge.els.get(z.id);
      if (!el) continue;
      el.style.opacity = z.id === zone.id ? String(Math.max(0, eased)) : "0";
    }
  });

  return null;
}

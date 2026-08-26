"use client";

import { ZONES } from "@/lib/zones";
import { zoneOverlayBridge } from "@/lib/zoneOverlayBridge";

// Rendered as a plain HTML sibling outside the <Canvas> (like Talk-Back),
// not inside drei's <Scroll html> — see zoneOverlayBridge.ts for the
// real crash that caused this. Opacity is driven imperatively by
// ZoneOverlaySync (mounted inside <ScrollControls>) via the refs
// registered below; both it and CameraRig read the same ZONES source of
// truth, so the label on screen always names the zone the camera is
// actually looking at.
export function ZoneOverlay() {
  return (
    <div className="zone-overlay">
      {ZONES.filter((zone) => zone.id !== "entry").map((zone, i) => (
        <div
          key={zone.id}
          ref={(el) => {
            if (el) zoneOverlayBridge.els.set(zone.id, el);
          }}
          className="zone-overlay-label"
          style={{ opacity: 0 }}
        >
          <div className="zone-overlay-index">
            {String(i + 1).padStart(2, "0")} / {String(ZONES.length - 1).padStart(2, "0")}
          </div>
          <div className="zone-overlay-eyebrow">{zone.eyebrow}</div>
        </div>
      ))}
    </div>
  );
}

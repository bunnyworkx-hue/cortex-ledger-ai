"use client";

import { Scroll } from "@react-three/drei";
import { ZONES } from "@/lib/zones";

// Rendered inside <Scroll html>, which drei positions in the same
// scroll-page coordinate space the camera rig reads via useScroll() —
// both derive from the same ZONES source of truth, so the label that's
// on screen always names the zone the camera is actually looking at.
export function ZoneOverlay({ pages }: { pages: number }) {
  return (
    <Scroll html>
      {ZONES.map((zone) => (
        <div
          key={zone.id}
          style={{
            position: "absolute",
            top: `${zone.start * pages * 100}vh`,
            height: `${(zone.end - zone.start) * pages * 100}vh`,
            width: "100vw",
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-end",
            padding: "0 0 14vh 6vw",
            pointerEvents: "none",
          }}
        >
          {zone.id !== "entry" && (
            <div style={{ maxWidth: 520 }}>
              <div
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 11,
                  letterSpacing: "0.14em",
                  color: "#8791E8",
                  marginBottom: 6,
                }}
              >
                {String(ZONES.indexOf(zone)).padStart(2, "0")} / {String(ZONES.length - 1).padStart(2, "0")}
              </div>
              <div
                style={{
                  fontFamily: "'IBM Plex Sans', sans-serif",
                  fontSize: 13,
                  color: "#9aa0c9",
                  lineHeight: 1.5,
                }}
              >
                {zone.eyebrow}
              </div>
            </div>
          )}
        </div>
      ))}
    </Scroll>
  );
}

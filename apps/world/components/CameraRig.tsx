"use client";

import { useScroll } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import { Vector3 } from "three";
import { ZONES } from "@/lib/zones";

type Keyframe = { t: number; position: [number, number, number]; target: [number, number, number] };

// Two keyframes per zone (at start and end) so the camera settles for
// the zone's dwell period instead of drifting continuously — the same
// "ease in, hold, ease to next" pacing real scrollytelling pages use.
const KEYFRAMES: Keyframe[] = ZONES.flatMap((zone) => [
  { t: zone.start, position: zone.cameraPosition, target: zone.cameraTarget },
  { t: zone.end, position: zone.cameraPosition, target: zone.cameraTarget },
]);

function sampleKeyframes(scroll: number): { position: Vector3; target: Vector3 } {
  if (scroll <= KEYFRAMES[0].t) {
    return { position: new Vector3(...KEYFRAMES[0].position), target: new Vector3(...KEYFRAMES[0].target) };
  }
  for (let i = 0; i < KEYFRAMES.length - 1; i++) {
    const a = KEYFRAMES[i];
    const b = KEYFRAMES[i + 1];
    if (scroll >= a.t && scroll <= b.t) {
      const span = b.t - a.t || 1;
      const localT = (scroll - a.t) / span;
      const eased = localT * localT * (3 - 2 * localT); // smoothstep
      return {
        position: new Vector3(...a.position).lerp(new Vector3(...b.position), eased),
        target: new Vector3(...a.target).lerp(new Vector3(...b.target), eased),
      };
    }
  }
  const last = KEYFRAMES[KEYFRAMES.length - 1];
  return { position: new Vector3(...last.position), target: new Vector3(...last.target) };
}

export function CameraRig() {
  const scroll = useScroll();
  const currentTarget = useRef(new Vector3(...ZONES[0].cameraTarget));

  useFrame((state, delta) => {
    const { position, target } = sampleKeyframes(scroll.offset);
    // Damped follow rather than snapping straight to the sampled point —
    // this is what makes scroll feel like it's driving a real camera
    // instead of teleporting between poses every frame.
    const damping = 1 - Math.pow(0.001, delta);
    state.camera.position.lerp(position, damping);
    currentTarget.current.lerp(target, damping);
    state.camera.lookAt(currentTarget.current);
  });

  return null;
}

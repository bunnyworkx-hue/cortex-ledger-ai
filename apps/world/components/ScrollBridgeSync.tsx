"use client";

import { useScroll } from "@react-three/drei";
import { useEffect } from "react";
import { scrollBridge } from "@/lib/scrollBridge";

/** Mounted inside <ScrollControls> — publishes the real scroll element
 * so the outside-the-Canvas Talk-Back bar can drive scroll position. */
export function ScrollBridgeSync() {
  const scroll = useScroll();
  useEffect(() => {
    scrollBridge.el = scroll.el;
    return () => {
      scrollBridge.el = null;
    };
  }, [scroll.el]);
  return null;
}

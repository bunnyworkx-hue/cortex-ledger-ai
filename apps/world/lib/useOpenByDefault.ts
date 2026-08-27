"use client";

import { useState, useSyncExternalStore, type Dispatch, type SetStateAction } from "react";

// AgentListPanel and GraphNodeListPanel both default open on desktop —
// they exist specifically to compensate for their 3D clusters spinning
// continuously, so hiding them by default there would reintroduce the
// exact problem they were built to solve. But at a real phone width
// there isn't room for two persistent side panels plus Talk-Back without
// them overlapping, so they default closed there instead.
//
// Reads viewport width via useSyncExternalStore rather than
// useEffect+setState: the latter is a real anti-pattern (an unconditional
// setState in a mount effect causes a synchronous extra render), and a
// naive `useState(() => window.innerWidth < N)` would read `window`
// during the server render and mismatch the client's first hydration
// pass. useSyncExternalStore is the pattern React itself provides for
// exactly this — subscribing to external, non-React state that differs
// between server and client — and it re-renders the real client value in
// automatically right after hydration, with no user-authored effect.
const NARROW_VIEWPORT_QUERY = "(max-width: 767px)";

function subscribe(callback: () => void) {
  const mql = window.matchMedia(NARROW_VIEWPORT_QUERY);
  mql.addEventListener("change", callback);
  return () => mql.removeEventListener("change", callback);
}
function getSnapshot() {
  return window.matchMedia(NARROW_VIEWPORT_QUERY).matches;
}
function getServerSnapshot() {
  return false;
}

export function useOpenByDefault(): [boolean, Dispatch<SetStateAction<boolean>>] {
  const isNarrow = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  // null = user hasn't touched the toggle yet — follow the viewport default.
  const [userChoice, setUserChoice] = useState<boolean | null>(null);
  const open = userChoice ?? !isNarrow;

  const setOpen: Dispatch<SetStateAction<boolean>> = (value) => {
    setUserChoice((prev) => {
      const current = prev ?? !isNarrow;
      return typeof value === "function" ? (value as (p: boolean) => boolean)(current) : value;
    });
  };

  return [open, setOpen];
}

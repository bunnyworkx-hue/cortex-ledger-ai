// A real bug forced this file into existence: drei's <Scroll html> (the
// original mechanism for the zone-label overlay) calls
// ReactDOMClient.createRoot() internally to portal HTML content outside
// the R3F canvas tree, and it doesn't survive React 19 Strict Mode's
// deliberate double-invoke of effects in Next.js dev mode — a real
// "createRoot() on a container that has already been passed to
// createRoot()" crash, confirmed live in the browser, not a guess.
//
// Fix: render the zone labels as plain HTML outside the Canvas entirely
// (a normal sibling, like Talk-Back) and drive their opacity
// imperatively from inside the R3F tree via refs registered here —
// matching CameraRig's own pattern of never putting high-frequency
// scroll-driven updates through React state/re-renders.
export const zoneOverlayBridge: { els: Map<string, HTMLDivElement> } = { els: new Map() };

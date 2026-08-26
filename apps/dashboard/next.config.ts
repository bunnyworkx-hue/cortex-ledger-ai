import type { NextConfig } from "next";

// The dashboard's client-side code calls the Axiom API through this
// server (same-origin, /api/*) instead of fetching http://127.0.0.1:8000
// directly from the browser. A direct cross-origin browser fetch is what
// the CORS middleware in apps/api was for, but it turned out to be a
// real point of fragility in practice (ad-blockers / privacy extensions
// / embedded-webview contexts can silently block a fetch to a
// non-standard local port even when CORS itself is configured
// correctly — confirmed live: every server-side check, including a
// simulated browser preflight with the right Origin header, came back
// clean, yet the browser's own fetch still failed). Proxying through
// Next's own server sidesteps that whole class of problem: the browser
// only ever talks to its own origin, and Next's Node process (running
// on the same machine as the API, exactly like `curl` does) makes the
// real request to 127.0.0.1:8000 instead.
const AXIOM_API_ORIGIN = process.env.AXIOM_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${AXIOM_API_ORIGIN}/:path*` }];
  },
};

export default nextConfig;

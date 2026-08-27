import type { NextConfig } from "next";

// The browser calls this server's own same-origin /api/* path, which
// app/api/[...path]/route.ts proxies server-side to the real Cortex Ledger AI API
// (AXIOM_API_ORIGIN) — same-origin to avoid a real cross-origin fetch
// failure hit live (see that route handler's comment for the full
// story, and for why it's a real route handler rather than
// next.config.ts's built-in rewrites(), which this app used originally
// but had an undocumented ~30s timeout — a real bug found live in
// apps/world's identical setup).
const nextConfig: NextConfig = {};

export default nextConfig;

import type { NextConfig } from "next";

// The browser calls this server's own same-origin /api/* path, which
// app/api/[...path]/route.ts proxies server-side to the real Cortex Ledger AI API
// (AXIOM_API_ORIGIN) — a real, explicit route handler rather than
// next.config.ts's built-in rewrites(), which this app used originally
// but had an undocumented ~30s timeout that cut off genuinely
// successful, slower real calls (Hermes delegations routinely take
// 10-35s+). See the route handler's own comment for the full story.
const nextConfig: NextConfig = {};

export default nextConfig;

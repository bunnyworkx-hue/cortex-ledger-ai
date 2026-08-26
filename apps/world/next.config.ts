import type { NextConfig } from "next";

// Same pattern as apps/dashboard/next.config.ts (see its comment for the
// full rationale): the browser calls this server's own same-origin
// /api/* path, which Next proxies server-side to the real Axiom API.
const AXIOM_API_ORIGIN = process.env.AXIOM_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${AXIOM_API_ORIGIN}/:path*` }];
  },
};

export default nextConfig;

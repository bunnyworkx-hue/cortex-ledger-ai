import { NextRequest, NextResponse } from "next/server";

// Real bug found live in apps/world (identical rewrite pattern there):
// next.config.ts's rewrites()-based proxy (Next's own built-in
// mechanism) has an undocumented ~30s timeout that cut off a genuinely
// successful real Hermes delegation mid-flight — confirmed
// reproducibly, the identical request succeeded hitting the API
// directly but failed with an empty 500 at exactly ~30s through the
// rewrite every time. The dashboard doesn't call Hermes today, but it
// shares this exact proxy mechanism, so it carries the same latent
// ceiling for any slow real call — fixed here too rather than left
// duplicated and unfixed.
//
// Replaces next.config.ts's rewrites() with an explicit route handler
// that controls its own timeout — set to comfortably exceed
// HermesBackend's own real default (120s, packages/axiom-hermes/
// axiom_hermes/adapter.py).
const AXIOM_API_ORIGIN = process.env.AXIOM_API_ORIGIN ?? "http://127.0.0.1:8000";
const PROXY_TIMEOUT_MS = 130_000;

async function proxy(req: NextRequest, path: string[]): Promise<NextResponse> {
  const target = `${AXIOM_API_ORIGIN}/${path.join("/")}${req.nextUrl.search}`;
  const hasBody = req.method !== "GET" && req.method !== "HEAD";

  try {
    const response = await fetch(target, {
      method: req.method,
      headers: { "content-type": req.headers.get("content-type") ?? "application/json" },
      body: hasBody ? await req.text() : undefined,
      signal: AbortSignal.timeout(PROXY_TIMEOUT_MS),
      cache: "no-store",
    });
    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch (err) {
    const timedOut = err instanceof Error && err.name === "TimeoutError";
    return NextResponse.json(
      {
        detail: timedOut
          ? `Cortex Ledger AI API did not respond within ${PROXY_TIMEOUT_MS / 1000}s`
          : `Could not reach the Cortex Ledger AI API at ${AXIOM_API_ORIGIN}`,
      },
      { status: 502 }
    );
  }
}

type RouteParams = { params: Promise<{ path: string[] }> };

export async function GET(req: NextRequest, { params }: RouteParams) {
  return proxy(req, (await params).path);
}
export async function POST(req: NextRequest, { params }: RouteParams) {
  return proxy(req, (await params).path);
}
export async function PUT(req: NextRequest, { params }: RouteParams) {
  return proxy(req, (await params).path);
}
export async function PATCH(req: NextRequest, { params }: RouteParams) {
  return proxy(req, (await params).path);
}
export async function DELETE(req: NextRequest, { params }: RouteParams) {
  return proxy(req, (await params).path);
}

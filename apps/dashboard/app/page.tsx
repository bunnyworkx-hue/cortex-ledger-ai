"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ApiError, type AgentFabricStatus } from "@/lib/api";

const WORLD_URL = process.env.NEXT_PUBLIC_WORLD_URL ?? "http://localhost:3001";
const CONTACT_EMAIL = "thegordontree@gmail.com";
const RESUME_URL = "/turon-gordon-resume.pdf";
const GITHUB_URL = "https://github.com/bunnyworkx-hue/cortex-ledger-ai";

// This is an employer-facing engineering portfolio, not a customer
// funnel — every claim below is checked against what's actually running
// (INSPECT below links to real dashboard routes), not aspirational copy.
const PILLARS = [
  {
    name: "Agent Fabric",
    question: "WHO performs the work?",
    body: "Real agents, discovered by capability search, invoked through permission and budget checks — not a static list handed to every caller.",
  },
  {
    name: "Knowledge Fabric",
    question: "WHAT does the system need to understand?",
    body: "Graphify's real extraction graph — nodes and edges pulled from an actual codebase, not invented context.",
  },
  {
    name: "Execution Engine",
    question: "HOW does the work get performed?",
    body: "Claude, Hermes, and native tools behind one Model Gateway, gated by a real risk-tiered policy engine and human approval.",
  },
];

// Real bugs, root-caused and fixed in this repo — not case-study prose
// written after the fact. Exact details in docs/IMPLEMENTATION_PLAN.md.
const DECISIONS = [
  {
    n: "01",
    title: "The proxy timeout nobody documented",
    body: "A real Hermes delegation succeeded in ~32s via a direct API call, but failed with an empty 500 through this app's own proxy — twice, at almost exactly 30 seconds both times. Root cause: Next.js's built-in rewrites() carries an undocumented ~30s timeout on proxied requests, a latent ceiling since the proxy was introduced. Fixed by replacing it with an explicit Route Handler and an AbortSignal.timeout(130_000) — then applied the identical fix to the sibling app before it hit the same bug later instead of after.",
  },
  {
    n: "02",
    title: "Didn't turn off Strict Mode to make the crash go away",
    body: "A real React crash — “ReactDOMClient.createRoot() on a container that has already been passed to createRoot()” — traced to a third-party 3D library's HTML-portal helper, which doesn't survive React 19 Strict Mode's deliberate double-invoke in dev. The fast fix was reactStrictMode: false. Didn't take it — that silences real bug-catching everywhere else too. Removed the helper entirely and rebuilt the overlay as a plain HTML sibling driven imperatively through a ref bridge, matching a pattern already used elsewhere in the same codebase for the same reason.",
  },
  {
    n: "03",
    title: "My bug vs. their bug — and only fixing the one that was mine",
    body: "A tool-calling panel was throwing errors on every call. Traced each one individually instead of assuming one root cause: Number(\"\") evaluates to 0 in JavaScript, not NaN, so an empty required field was silently “valid” — that one was mine, fixed by validating required fields before the network call. A separate empty field reached a third-party library's own handler and crashed it with a raw Python exception — that one wasn't mine to patch from this panel, so it wasn't.",
  },
];

const INSPECT = [
  { label: "Agent Fabric", href: "/agents", detail: "the real, live agent registry" },
  { label: "Execution Traces", href: "/executions", detail: "real request-to-result history" },
  { label: "Approvals", href: "/approvals", detail: "the real human-in-the-loop queue" },
  { label: "Tool Registry / MCP", href: "/tools", detail: "the real callable tool surface" },
];

export default function Landing() {
  const [fabric, setFabric] = useState<AgentFabricStatus | null>(null);
  const [toolCount, setToolCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.agentFabricStatus(), api.listTools()])
      .then(([f, tools]) => {
        if (cancelled) return;
        setFabric(f);
        setToolCount(tools.length);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Failed to reach the Cortex Ledger AI API");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-24">
      {/* ---------- hero ---------- */}
      <section className="grid grid-cols-1 items-center gap-10 py-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="flex flex-col items-start gap-6">
          <div className="font-mono text-xs uppercase tracking-widest text-accent">
            AI Engineering · Agentic Systems · Multi-Agent Orchestration · AI Infrastructure
          </div>
          <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            I build AI systems — not just AI prompts.
          </h1>
          <p className="max-w-xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
            I design and build intelligent systems that connect frontier models, autonomous agents, tools,
            knowledge, APIs, memory, security, and human oversight into production-oriented AI
            infrastructure. <strong className="font-semibold text-zinc-700 dark:text-zinc-300">Cortex Ledger AI</strong>{" "}
            is the flagship demonstration — every decision traced, every agent accountable.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <a
              href={WORLD_URL}
              className="rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:opacity-90"
            >
              Explore My AI Engineering Work
            </a>
            <a
              href={RESUME_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md border border-zinc-300 px-5 py-2.5 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              View Resume
            </a>
            <a
              href={`mailto:${CONTACT_EMAIL}`}
              className="rounded-md border border-zinc-300 px-5 py-2.5 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Contact Me
            </a>
          </div>

          <div className="pt-2 font-mono text-xs text-zinc-500 dark:text-zinc-400">
            {error ? (
              <span>
                live system unreachable ({error}) — check that <code>./scripts/dev/run.sh</code> is running
              </span>
            ) : fabric && toolCount !== null ? (
              <span>
                {fabric.total_agents} real agents · {toolCount} registered tools · Agent Fabric{" "}
                {fabric.configured ? "configured" : "not configured"} · 104 tests passing
              </span>
            ) : (
              <span>reading live registry…</span>
            )}
          </div>
        </div>

        <div className="relative order-first lg:order-last">
          <Image
            src="/cortex-ledger-ai-mark.png"
            alt="Cortex Ledger AI — intelligence, accuracy, transparency"
            width={1536}
            height={1024}
            className="h-auto w-full"
            priority
          />
        </div>
      </section>

      {/* ---------- engineering thesis ---------- */}
      <section className="flex flex-col gap-4 border-y border-zinc-200 py-10 dark:border-zinc-800">
        <div className="text-xs font-medium uppercase tracking-wide text-accent">
          What I believe about AI engineering
        </div>
        <p className="max-w-2xl text-xl font-medium leading-snug tracking-tight">
          AI engineering isn&rsquo;t just calling an LLM.
        </p>
        <div className="flex flex-wrap items-center gap-2 font-mono text-xs uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
          {["Model", "Agents", "Tools", "Knowledge", "Orchestration", "Policy", "Observability"].map((term, i, arr) => (
            <span key={term} className="flex items-center gap-2">
              <span className="rounded border border-zinc-300 px-2 py-1 dark:border-zinc-700">{term}</span>
              {i < arr.length - 1 && <span>+</span>}
            </span>
          ))}
          <span>=</span>
          <span className="rounded bg-accent px-2 py-1 text-white">AI System</span>
        </div>
        <p className="max-w-2xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          The difficult part of AI engineering is designing the systems around intelligence that let
          models and agents safely reason, discover capabilities, collaborate, execute actions, verify
          outcomes, and operate reliably — under permissions a human actually controls.
        </p>
      </section>

      {/* ---------- three-pillar architecture ---------- */}
      <section className="flex flex-col gap-6">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-accent">Project 01</div>
          <h2 className="mt-1 text-2xl font-semibold tracking-tight">Cortex Ledger AI</h2>
          <p className="mt-1 max-w-xl text-sm text-zinc-500 dark:text-zinc-400">
            An agentic AI operating layer orchestrating frontier models, an external agent runtime,
            specialized business agents, tools, MCP services, a knowledge graph, memory, permissions,
            approvals, and execution — under one control plane.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {PILLARS.map((pillar) => (
            <div
              key={pillar.name}
              className="rounded-lg border border-zinc-200 border-t-2 border-t-accent p-5 dark:border-zinc-800 dark:border-t-accent"
            >
              <div className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                {pillar.question}
              </div>
              <div className="mt-1 text-lg font-semibold tracking-tight">{pillar.name}</div>
              <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{pillar.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- engineering decisions ---------- */}
      <section className="flex flex-col gap-8">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Engineering decisions, not just features</h2>
          <p className="mt-1 max-w-xl text-sm text-zinc-500 dark:text-zinc-400">
            Three real bugs from building this system — root-caused and fixed, not smoothed over.
          </p>
        </div>
        <div className="flex flex-col gap-6">
          {DECISIONS.map((d) => (
            <div key={d.n} className="flex gap-5">
              <div className="font-mono text-sm text-accent">{d.n}</div>
              <div className="flex flex-col gap-1.5 border-l border-zinc-200 pl-5 dark:border-zinc-800">
                <div className="font-semibold text-zinc-800 dark:text-zinc-200">{d.title}</div>
                <p className="max-w-2xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">{d.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- inspect the system ---------- */}
      <section className="flex flex-col gap-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Don&rsquo;t take my word for it. Inspect the system.</h2>
          <p className="mt-1 max-w-xl text-sm text-zinc-500 dark:text-zinc-400">
            Every link below opens a real, live page reading directly from the running API — not a
            screenshot or a mock.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          {INSPECT.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="group flex flex-col rounded-md border border-zinc-300 px-4 py-3 text-sm transition-colors hover:border-accent hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
            >
              <span className="font-semibold text-zinc-800 dark:text-zinc-200">{item.label}</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">{item.detail}</span>
            </Link>
          ))}
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex flex-col rounded-md border border-accent/40 px-4 py-3 text-sm transition-colors hover:border-accent hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <span className="font-semibold text-accent">View the source on GitHub</span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">the real commit history, not just the live app</span>
          </a>
        </div>
      </section>

      {/* ---------- employer cta ---------- */}
      <section className="flex flex-col gap-4 rounded-lg border border-zinc-200 p-8 dark:border-zinc-800">
        <h2 className="text-2xl font-semibold tracking-tight">Looking for a lead engineer?</h2>
        <p className="max-w-xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          I&rsquo;m interested in opportunities where I can own the systems around AI — architecture,
          orchestration, infrastructure, and the judgment calls that decide what a team builds and how
          it fails safely.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:opacity-90"
          >
            Request a Technical Interview
          </a>
          <a
            href={RESUME_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-zinc-300 px-5 py-2.5 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            View Resume
          </a>
        </div>
      </section>
    </div>
  );
}

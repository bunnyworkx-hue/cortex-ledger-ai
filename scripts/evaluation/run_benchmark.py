#!/usr/bin/env python3
"""Milestone 19 — Cortex Ledger AI evaluation benchmark (CLAUDE.md §75).

Runs a real 20-task benchmark against a REAL, already-running Cortex Ledger AI API
(default http://127.0.0.1:8000) — every task is a genuine HTTP call
through the same endpoints a real client would use (delegate, tool call,
approval flow). Nothing here calls Python internals directly and nothing
is simulated: a task fails if the real backend fails.

Scoring is deliberately simple and honest (CLAUDE.md §45/§75: "never
fabricate metrics"). Most tasks ask an agent to reply with an exact,
unambiguous token ("reply with exactly: <token>") — a real, deterministic
end-to-end check that the whole pipeline (Agent Fabric -> Backend ->
Model -> real response) still works, not a fuzzy judgment of output
quality. Tool/knowledge/approval tasks check for a real structural
signal (a field present, a substring in real tool output) instead.

Usage:
    uv run python scripts/evaluation/run_benchmark.py [--api-url URL]

Writes a JSON report to var/evaluation/run_<timestamp>.json (gitignored,
like every other generated artifact in var/) so results are comparable
across runs (CLAUDE.md §73's "regression testing") without inventing a
new database table for it.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class BenchmarkTask:
    id: str
    category: str
    description: str
    run: Callable[[httpx.Client], "TaskOutcome"]


@dataclass(slots=True)
class TaskOutcome:
    passed: bool
    detail: str


@dataclass(slots=True)
class TaskResult:
    task_id: str
    category: str
    description: str
    passed: bool
    detail: str
    duration_ms: float


def _delegate_exact_reply(agent_id: str, token: str, *, backend: str | None = None):
    def run(client: httpx.Client) -> TaskOutcome:
        response = client.post(
            f"/v1/agent-fabric/agents/{agent_id}/delegate",
            json={"input": f"Reply with exactly: {token}", "backend": backend},
        )
        if response.status_code != 200:
            return TaskOutcome(False, f"HTTP {response.status_code}: {response.text[:200]}")
        content = (response.json().get("content") or "").strip()
        passed = token.lower() in content.lower()
        return TaskOutcome(passed, f"expected {token!r} in reply, got {content!r}")

    return run


def _tool_call_contains(tool_name: str, arguments: dict, expect_substring: str):
    def run(client: httpx.Client) -> TaskOutcome:
        response = client.post(f"/v1/tools/{tool_name}/call", json={"arguments": arguments})
        if response.status_code != 200:
            return TaskOutcome(False, f"HTTP {response.status_code}: {response.text[:200]}")
        body = response.json()
        text = json.dumps(body.get("content", {})).lower()
        passed = expect_substring.lower() in text and not body.get("is_error", False)
        return TaskOutcome(passed, f"expected {expect_substring!r} in tool output")

    return run


def _make_approval_flow_task():
    def run(client: httpx.Client) -> TaskOutcome:
        record_id = f"benchmark-{int(time.time())}"
        propose = client.post(
            "/v1/tools/modify_business_record/call",
            json={"arguments": {"record_id": record_id, "fields": {"status": "benchmark"}}},
        )
        if propose.status_code != 200 or "approval_id" not in propose.json():
            return TaskOutcome(False, f"propose did not yield a pending approval: {propose.text[:200]}")
        approval_id = propose.json()["approval_id"]

        approve = client.post(
            f"/v1/approvals/{approval_id}/approve", json={"decided_by": "evaluation-benchmark"}
        )
        if approve.status_code != 200:
            return TaskOutcome(False, f"approve failed: HTTP {approve.status_code}: {approve.text[:200]}")

        record = approve.json().get("content", {}).get("record", {})
        passed = record.get("status") == "benchmark"
        return TaskOutcome(passed, f"record after approval: {record}")

    return run


def build_tasks() -> list[BenchmarkTask]:
    return [
        # research
        BenchmarkTask("research-1", "research", "Frontend Developer research ack",
                      _delegate_exact_reply("engineering/engineering-frontend-developer", "research-ack-1")),
        BenchmarkTask("research-2", "research", "Spatial Data Scientist research ack",
                      _delegate_exact_reply("gis/gis-spatial-data-scientist", "research-ack-2")),
        # analysis
        BenchmarkTask("analysis-1", "analysis", "FP&A Analyst analysis ack",
                      _delegate_exact_reply("finance/finance-fpa-analyst", "analysis-ack-1")),
        BenchmarkTask("analysis-2", "analysis", "AppSec Engineer analysis ack",
                      _delegate_exact_reply("security/security-appsec-engineer", "analysis-ack-2")),
        # planning
        BenchmarkTask("planning-1", "planning", "Project Shepherd planning ack",
                      _delegate_exact_reply("project-management/project-management-project-shepherd", "planning-ack-1")),
        BenchmarkTask("planning-2", "planning", "Product Manager planning ack",
                      _delegate_exact_reply("product/product-manager", "planning-ack-2")),
        # marketing
        BenchmarkTask("marketing-1", "marketing", "SEO Specialist marketing ack",
                      _delegate_exact_reply("marketing/marketing-seo-specialist", "marketing-ack-1")),
        BenchmarkTask("marketing-2", "marketing", "UX Architect marketing ack",
                      _delegate_exact_reply("design/design-ux-architect", "marketing-ack-2")),
        # finance
        BenchmarkTask("finance-1", "finance", "FP&A Analyst finance ack",
                      _delegate_exact_reply("finance/finance-fpa-analyst", "finance-ack-1")),
        BenchmarkTask("finance-2", "finance", "Deal Strategist finance ack",
                      _delegate_exact_reply("sales/sales-deal-strategist", "finance-ack-2")),
        # operations
        BenchmarkTask("operations-1", "operations", "Project Shepherd operations ack",
                      _delegate_exact_reply("project-management/project-management-project-shepherd", "operations-ack-1")),
        BenchmarkTask("operations-2", "operations", "Support Responder operations ack",
                      _delegate_exact_reply("support/support-support-responder", "operations-ack-2")),
        # agent_delegation
        BenchmarkTask("agent-delegation-1", "agent_delegation", "Software Architect delegation ack",
                      _delegate_exact_reply("engineering/engineering-software-architect", "delegation-ack-1")),
        BenchmarkTask("agent-delegation-2", "agent_delegation", "Test Automation Engineer delegation ack",
                      _delegate_exact_reply("testing/testing-test-automation-engineer", "delegation-ack-2")),
        # hermes_delegation
        BenchmarkTask("hermes-delegation-1", "hermes_delegation", "Frontend Developer via Hermes",
                      _delegate_exact_reply("engineering/engineering-frontend-developer", "hermes-ack-1", backend="hermes")),
        BenchmarkTask("hermes-delegation-2", "hermes_delegation", "Deal Strategist via Hermes",
                      _delegate_exact_reply("sales/sales-deal-strategist", "hermes-ack-2", backend="hermes")),
        # tool_use
        BenchmarkTask("tool-use-1", "tool_use", "graph_stats reports real node count",
                      _tool_call_contains("graph_stats", {}, "nodes")),
        # knowledge_query
        BenchmarkTask("knowledge-query-1", "knowledge_query", "query_graph finds Frontend Developer",
                      _tool_call_contains("query_graph", {"question": "frontend developer"}, "frontend")),
        # graphify_query
        BenchmarkTask("graphify-query-1", "graphify_query", "get_node returns the real node",
                      _tool_call_contains("get_node", {"label": "Frontend Developer"}, "Frontend Developer")),
        # human_approval
        BenchmarkTask("human-approval-1", "human_approval", "propose -> approve -> real execution",
                      _make_approval_flow_task()),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    tasks = build_tasks()
    results: list[TaskResult] = []

    with httpx.Client(base_url=args.api_url, timeout=60.0) as client:
        for task in tasks:
            started = time.monotonic()
            try:
                outcome = task.run(client)
            except httpx.HTTPError as exc:
                outcome = TaskOutcome(False, f"HTTP error: {exc}")
            duration_ms = (time.monotonic() - started) * 1000
            results.append(
                TaskResult(task.id, task.category, task.description, outcome.passed, outcome.detail, duration_ms)
            )
            mark = "PASS" if outcome.passed else "FAIL"
            print(f"[{mark}] {task.id:<24} {task.category:<18} {duration_ms:>7.0f}ms  {outcome.detail[:80]}")

    passed_count = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{passed_count}/{total} passed ({round(100 * passed_count / total)}%)")

    report = {
        "run_at": datetime.now(UTC).isoformat(),
        "api_url": args.api_url,
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "results": [
            {
                "task_id": r.task_id,
                "category": r.category,
                "description": r.description,
                "passed": r.passed,
                "detail": r.detail,
                "duration_ms": round(r.duration_ms, 1),
            }
            for r in results
        ],
    }
    out_dir = REPO_ROOT / "var" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"run_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Report written to {out_path.relative_to(REPO_ROOT)}")

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())

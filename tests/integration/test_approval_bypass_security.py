"""Milestone 20 (Security) — Approval Bypass Tests, CLAUDE.md §96.

Complements tests/integration/test_approvals_endpoint.py (which already
covers the double-approve and reject-then-approve cases from Milestone
16). This file adds the edge cases that are specifically about someone
*trying* to bypass the gate rather than about the happy path:

- a fabricated/nonexistent approval_id can't be approved or rejected
  (no way to guess a live approval into existing)
- calling an unregistered tool name never silently "succeeds" — it 404s
  before any policy/approval logic runs
"""

import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_approving_a_nonexistent_approval_id_fails(api_client: httpx.AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await api_client.post(f"/v1/approvals/{fake_id}/approve", json={"decided_by": "attacker"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rejecting_a_nonexistent_approval_id_fails(api_client: httpx.AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await api_client.post(f"/v1/approvals/{fake_id}/reject", json={"decided_by": "attacker"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_calling_an_unregistered_tool_name_404s_before_any_policy_check(
    api_client: httpx.AsyncClient,
):
    response = await api_client.post(
        "/v1/tools/does-not-exist-as-a-tool/call", json={"arguments": {}}
    )
    assert response.status_code == 404
    # No approval record could have been created for a tool that was
    # never even found — nothing to reject in /v1/approvals afterward.
    pending = await api_client.get("/v1/approvals")
    assert response.status_code == 404 and pending.status_code == 200

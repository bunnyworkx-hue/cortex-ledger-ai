"""Milestone 20 (Security) — Memory/Tenant Isolation Tests, CLAUDE.md §96.

Honest finding, not a passing "isolation works" test: ``MemoryRecord``
carries ``owner_id``/``tenant_id`` fields and ``GET /v1/memory`` accepts
them as filters (apps/api/axiom_api/routers/memory.py), but neither value
is derived from any authenticated caller identity — there is no auth
layer in this build at all (see docs/security/SECURITY_AUDIT.md). The
caller supplies whatever ``owner_id``/``tenant_id`` it wants as plain
query parameters, so anyone who can reach the API can read anyone else's
memory records by guessing or knowing their owner_id.

This test proves that current, real behavior (it passes today precisely
*because* the gap exists) so it acts as a tripwire: if someone adds real
per-caller access control later without updating this test, the test
will start failing loudly instead of the change going unnoticed.
"""

import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_any_caller_can_read_another_owners_memory_by_owner_id(
    api_client: httpx.AsyncClient,
):
    victim_owner = f"victim-{uuid.uuid4()}"

    save = await api_client.post(
        "/v1/memory",
        json={
            "scope": "task",
            "owner_id": victim_owner,
            "content": "secret note belonging to the victim owner",
            "source": "pytest",
        },
    )
    if save.status_code == 503:
        pytest.skip("Memory store not configured in this environment")
    assert save.status_code == 200

    # A different, unrelated "attacker" caller simply asks for the
    # victim's owner_id — no credential, token, or prior relationship
    # required. This is the gap: nothing stops it.
    attacker_view = await api_client.get("/v1/memory", params={"owner_id": victim_owner})
    assert attacker_view.status_code == 200
    contents = [r["content"] for r in attacker_view.json()]
    assert "secret note belonging to the victim owner" in contents

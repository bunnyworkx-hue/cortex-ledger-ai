"""Milestone 20 (Security) — Memory/Tenant Isolation Tests, CLAUDE.md §96.

Milestone 20's original version of this file was a deliberate tripwire
proving a real gap: ``owner_id``/``tenant_id`` were caller-supplied query
parameters, not derived from any authenticated identity, so anyone could
read anyone else's memory by naming their owner_id. Milestone 22 closed
that gap for real (``apps/api/axiom_api/auth.py`` — a caller must present
a valid ``AXIOM_API_KEYS`` entry as ``Authorization: Bearer <key>``, and
``owner_id``/``tenant_id`` are derived from *which key was presented*,
never from the request). This file now proves the fix instead of the gap.
"""

import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_unauthenticated_caller_cannot_read_or_write_memory(api_client: httpx.AsyncClient):
    save = await api_client.post(
        "/v1/memory",
        json={"scope": "task", "content": "no auth header at all", "source": "pytest"},
    )
    if save.status_code == 503:
        pytest.skip("No AXIOM_API_KEYS configured in this environment")
    assert save.status_code == 401

    read = await api_client.get("/v1/memory")
    assert read.status_code == 401


@pytest.mark.asyncio
async def test_invalid_api_key_is_rejected(api_client: httpx.AsyncClient):
    read = await api_client.get("/v1/memory", headers={"Authorization": "Bearer not-a-real-key"})
    if read.status_code == 503:
        pytest.skip("No AXIOM_API_KEYS configured in this environment")
    assert read.status_code == 401


@pytest.mark.asyncio
async def test_a_caller_cannot_read_another_callers_memory_by_asking(
    api_client: httpx.AsyncClient,
):
    secret = f"secret note {uuid.uuid4()}"
    save = await api_client.post(
        "/v1/memory",
        json={"scope": "task", "content": secret, "source": "pytest"},
        headers={"Authorization": "Bearer dev-key-alice"},
    )
    if save.status_code in (503, 401):
        pytest.skip("AXIOM_API_KEYS not configured with dev-key-alice in this environment")
    assert save.status_code == 200
    assert save.json()["owner_id"] == "alice"

    # A different, real, valid caller (bob) — there is no owner_id
    # parameter left to ask for alice's records with; the gap this
    # closes is that one no longer exists as an input at all.
    attacker_view = await api_client.get("/v1/memory", headers={"Authorization": "Bearer dev-key-bob"})
    assert attacker_view.status_code == 200
    contents = [r["content"] for r in attacker_view.json()]
    assert secret not in contents

    # alice can read her own record back.
    owner_view = await api_client.get("/v1/memory", headers={"Authorization": "Bearer dev-key-alice"})
    assert owner_view.status_code == 200
    assert secret in [r["content"] for r in owner_view.json()]

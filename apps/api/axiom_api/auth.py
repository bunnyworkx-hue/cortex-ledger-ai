"""Milestone 22 — real caller-identity derivation for Memory/Tenant
Isolation, CLAUDE.md §96, closing the exact gap
``docs/security/SECURITY_AUDIT.md`` §6-7 documented and live-tested:
``GET``/``POST /v1/memory`` took ``owner_id``/``tenant_id`` as
caller-supplied strings, not values derived from any authenticated
identity, so any caller could read or write any other owner's records by
naming them.

Deliberately NOT a full user-account/session system — there's no login
flow, no ``User`` table, no JWTs anywhere in this codebase, and building
one is a real, separate, much larger feature. This is the minimum real
mechanism that actually closes the isolation gap: a caller must possess
a real, server-configured API key to be treated as a given owner, and
the server derives ``owner_id``/``tenant_id`` from *which key was
presented* — never from the request body or query string. A caller with
no key, or the wrong key, gets a real 401, not a degraded response.
"""

from dataclasses import dataclass

from fastapi import Header, HTTPException

from axiom_core.config import get_settings


@dataclass(frozen=True)
class AuthenticatedCaller:
    owner_id: str
    tenant_id: str | None


def _parse_api_keys(raw: str | None) -> dict[str, AuthenticatedCaller]:
    """``AXIOM_API_KEYS`` format: comma-separated ``key:owner_id`` or
    ``key:owner_id:tenant_id`` entries, e.g.
    ``demo-key:demo-user,ops-key:ops-user:ops-tenant``. Keys are secrets
    (server-side config, never sent to a client) — the string on the left
    of each ``:`` *is* the credential, not a username.
    """
    if not raw:
        return {}
    keys: dict[str, AuthenticatedCaller] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) < 2:
            continue
        key, owner_id = parts[0], parts[1]
        tenant_id = parts[2] if len(parts) > 2 and parts[2] else None
        keys[key] = AuthenticatedCaller(owner_id=owner_id, tenant_id=tenant_id)
    return keys


async def require_caller(authorization: str | None = Header(default=None)) -> AuthenticatedCaller:
    settings = get_settings()
    keys = _parse_api_keys(settings.api_keys)
    if not keys:
        raise HTTPException(
            status_code=503,
            detail="No API keys configured — set AXIOM_API_KEYS to enable authenticated endpoints.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header (expected 'Bearer <api-key>').",
        )
    key = authorization.removeprefix("Bearer ").strip()
    caller = keys.get(key)
    if caller is None:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return caller

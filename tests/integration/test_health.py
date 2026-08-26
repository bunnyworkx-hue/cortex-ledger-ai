import httpx
import pytest


@pytest.mark.asyncio
async def test_health_endpoint_responds(api_client: httpx.AsyncClient):
    response = await api_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "axiom-os"
    # Milestone 6 must report DB state honestly, not fake success —
    # "unconfigured" is a valid, expected result before AXIOM_DATABASE_URL
    # is set; "ok" once it's a real, reachable Supabase project.
    assert body["database"] in {"ok", "unconfigured"} or body["database"].startswith("error:")

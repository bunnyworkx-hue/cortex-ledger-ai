import httpx
import pytest


@pytest.mark.asyncio
async def test_status_reports_the_real_registry_honestly(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/agent-fabric")

    assert response.status_code == 200
    body = response.json()
    if body["configured"]:
        # A real AXIOM_AGENCY_AGENTS_PATH is set — this is the live path,
        # loaded from the real agency-agents corpus.
        assert body["total_agents"] > 200  # ~255 per AGENT_LIBRARY_AUDIT.md
        assert body["curated_agents"] == 12  # the curated cohort in curated.py
        assert "engineering" in body["by_division"]
    else:
        assert body["total_agents"] == 0


@pytest.mark.asyncio
async def test_list_agents_returns_the_full_real_roster(api_client: httpx.AsyncClient):
    status = (await api_client.get("/v1/agent-fabric")).json()
    if not status["configured"]:
        pytest.skip("AXIOM_AGENCY_AGENTS_PATH not set in this environment")

    response = await api_client.get("/v1/agent-fabric/agents")
    assert response.status_code == 200
    records = response.json()
    # The full roster, not just the 12 curated — every record has a real,
    # addressable agent_id and division, unlike GET /v1/agent-fabric's
    # aggregate-only counts.
    assert len(records) == status["total_agents"]
    assert any(r["agent_id"] == "engineering/engineering-frontend-developer" for r in records)
    assert all(r["agent_id"] and r["division"] for r in records)


@pytest.mark.asyncio
async def test_list_agents_filters_by_division(api_client: httpx.AsyncClient):
    status = (await api_client.get("/v1/agent-fabric")).json()
    if not status["configured"]:
        pytest.skip("AXIOM_AGENCY_AGENTS_PATH not set in this environment")

    response = await api_client.get("/v1/agent-fabric/agents", params={"division": "finance"})
    assert response.status_code == 200
    records = response.json()
    assert len(records) == status["by_division"]["finance"]
    assert all(r["division"] == "finance" for r in records)


@pytest.mark.asyncio
async def test_search_and_inspect_a_real_curated_agent(api_client: httpx.AsyncClient):
    status = (await api_client.get("/v1/agent-fabric")).json()
    if not status["configured"]:
        pytest.skip("AXIOM_AGENCY_AGENTS_PATH not set in this environment")

    search_response = await api_client.get(
        "/v1/agent-fabric/search", params={"q": "frontend react performance"}
    )
    assert search_response.status_code == 200
    results = search_response.json()
    assert any(r["agent_id"] == "engineering/engineering-frontend-developer" for r in results)

    inspect_response = await api_client.get(
        "/v1/agent-fabric/agents/engineering/engineering-frontend-developer"
    )
    assert inspect_response.status_code == 200
    detail = inspect_response.json()
    assert detail["name"] == "Frontend Developer"
    assert detail["is_curated"] is True
    assert "frontend_development" in detail["capabilities"]
    assert detail["source_commit"]
    assert "Frontend Developer" in detail["instructions"]


@pytest.mark.asyncio
async def test_inspect_unknown_agent_returns_404(api_client: httpx.AsyncClient):
    status = (await api_client.get("/v1/agent-fabric")).json()
    if not status["configured"]:
        pytest.skip("AXIOM_AGENCY_AGENTS_PATH not set in this environment")

    response = await api_client.get("/v1/agent-fabric/agents/does-not/exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delegate_to_a_real_curated_agent(api_client: httpx.AsyncClient):
    fabric_status = (await api_client.get("/v1/agent-fabric")).json()
    backend_status = (await api_client.get("/v1/agents")).json()["backends"]
    if not fabric_status["configured"] or "axiom_native" not in backend_status:
        pytest.skip("Agent Fabric or axiom_native backend not configured in this environment")

    response = await api_client.post(
        "/v1/agent-fabric/agents/engineering/engineering-frontend-developer/delegate",
        json={"input": "In one word, what do you build? Reply with exactly one word."},
    )

    # A real Task -> Registry -> Backend -> Execution -> Result round
    # trip. Either a genuine completion, or a clean 502 (e.g. no credit)
    # — never an uncaught 500.
    assert response.status_code in {200, 502}
    if response.status_code == 200:
        body = response.json()
        assert body["status"] == "succeeded"
        assert body["agent_id"] == "engineering/engineering-frontend-developer"
        assert body["content"]

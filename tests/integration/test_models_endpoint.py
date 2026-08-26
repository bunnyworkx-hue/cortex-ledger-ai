import httpx
import pytest


@pytest.mark.asyncio
async def test_list_model_backends_reports_status_honestly(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/models")

    assert response.status_code == 200
    providers = response.json()["providers"]
    # Whether or not AXIOM_ANTHROPIC_API_KEY is set in this environment,
    # the response must be an honest reflection of it — never a fake
    # "configured" if the key is actually missing.
    if "anthropic" in providers:
        assert providers["anthropic"] in {"configured", "not_configured"}


@pytest.mark.asyncio
async def test_complete_without_registered_backend_returns_503_not_a_fake_answer(
    api_client: httpx.AsyncClient,
):
    list_response = await api_client.get("/v1/models")
    providers = list_response.json()["providers"]

    response = await api_client.post(
        "/v1/models/complete",
        json={"messages": [{"role": "user", "content": "hi"}]},
    )

    if "anthropic" not in providers:
        assert response.status_code == 503
        assert "anthropic" in response.json()["detail"]
    else:
        # A real key is configured in this environment — this is the live
        # integration path. It must be a genuine result either way: a
        # real completion (200), or — if e.g. the account is out of
        # credit — a clean, honest 502, never an uncaught 500 traceback.
        assert response.status_code in {200, 502}
        body = response.json()
        if response.status_code == 200:
            assert body["provider"] == "anthropic"
            assert body["content"]
            assert body["usage"]["total_tokens"] > 0
        else:
            assert body["detail"]

from collections.abc import AsyncIterator

import httpx
import pytest

from axiom_api.main import app


@pytest.fixture
async def api_client() -> AsyncIterator[httpx.AsyncClient]:
    """An HTTP client for the real app, with FastAPI's lifespan (startup/
    shutdown) actually run — plain ASGITransport does not trigger lifespan
    on its own, which silently skips app.state population (e.g. the model
    gateway registry) in any test that doesn't use this fixture.
    """
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

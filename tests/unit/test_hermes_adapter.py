import pytest

import axiom_hermes.adapter as adapter_module
from axiom_core.agents import Agent, AgentBackendError, AgentTask
from axiom_hermes.adapter import HermesBackend
from axiom_hermes.client import HermesCliError, HermesRunResult, HermesTimeoutError


@pytest.mark.asyncio
async def test_is_configured_reflects_binary_presence():
    real_backend = HermesBackend("sk-fake", hermes_bin="python3")  # a binary that really exists
    missing_backend = HermesBackend("sk-fake", hermes_bin="definitely-not-a-real-binary-xyz")

    assert await real_backend.is_configured() is True
    assert await missing_backend.is_configured() is False


@pytest.mark.asyncio
async def test_execute_builds_prompt_and_injects_anthropic_key(monkeypatch):
    captured = {}

    async def fake_run_oneshot(hermes_bin, prompt, *, model, provider, env, timeout):
        captured["hermes_bin"] = hermes_bin
        captured["prompt"] = prompt
        captured["model"] = model
        captured["provider"] = provider
        captured["env"] = env
        return HermesRunResult(content="Hello!", usage={"estimated_cost_usd": 0.01})

    monkeypatch.setattr(adapter_module, "run_oneshot", fake_run_oneshot)

    backend = HermesBackend("sk-real-key", hermes_bin="hermes", default_model="anthropic/claude-sonnet-5")
    agent = Agent(agent_id="a1", name="Test Agent", instructions="You are a test agent.")
    task = AgentTask(input="say hi", context="The user's name is Sam.")

    result = await backend.execute(agent, task)

    assert result.content == "Hello!"
    assert result.raw == {"estimated_cost_usd": 0.01}
    assert captured["prompt"] == "You are a test agent.\n\nRelevant context:\nThe user's name is Sam.\n\nsay hi"
    assert captured["model"] == "anthropic/claude-sonnet-5"
    assert captured["provider"] == "anthropic"
    assert captured["env"]["ANTHROPIC_API_KEY"] == "sk-real-key"


@pytest.mark.asyncio
async def test_execute_translates_hermes_cli_error(monkeypatch):
    async def fake_run_oneshot(*args, **kwargs):
        raise HermesCliError("No usable credentials found for provider 'gmi'.")

    monkeypatch.setattr(adapter_module, "run_oneshot", fake_run_oneshot)

    backend = HermesBackend("sk-real-key")
    agent = Agent(agent_id="a1", name="Test Agent", instructions="You are a test agent.")

    with pytest.raises(AgentBackendError, match="No usable credentials"):
        await backend.execute(agent, AgentTask(input="say hi"))


@pytest.mark.asyncio
async def test_execute_overrides_default_timeout_with_agent_budget(monkeypatch):
    captured = {}

    async def fake_run_oneshot(hermes_bin, prompt, *, model, provider, env, timeout):
        captured["timeout"] = timeout
        return HermesRunResult(content="ok", usage={})

    monkeypatch.setattr(adapter_module, "run_oneshot", fake_run_oneshot)

    backend = HermesBackend("sk-real-key", timeout=120.0)
    agent = Agent(
        agent_id="a1", name="Test Agent", instructions="You are a test agent.", budget={"max_seconds": 30}
    )

    await backend.execute(agent, AgentTask(input="say hi"))

    assert captured["timeout"] == 30


@pytest.mark.asyncio
async def test_execute_without_budget_uses_instance_default_timeout(monkeypatch):
    captured = {}

    async def fake_run_oneshot(hermes_bin, prompt, *, model, provider, env, timeout):
        captured["timeout"] = timeout
        return HermesRunResult(content="ok", usage={})

    monkeypatch.setattr(adapter_module, "run_oneshot", fake_run_oneshot)

    backend = HermesBackend("sk-real-key", timeout=120.0)
    agent = Agent(agent_id="a1", name="Test Agent", instructions="You are a test agent.")

    await backend.execute(agent, AgentTask(input="say hi"))

    assert captured["timeout"] == 120.0


@pytest.mark.asyncio
async def test_execute_translates_hermes_timeout_into_budget_error(monkeypatch):
    async def fake_run_oneshot(*args, **kwargs):
        raise HermesTimeoutError("hermes -z did not finish within 0.01s")

    monkeypatch.setattr(adapter_module, "run_oneshot", fake_run_oneshot)

    backend = HermesBackend("sk-real-key")
    agent = Agent(
        agent_id="a1", name="Test Agent", instructions="You are a test agent.", budget={"max_seconds": 0.01}
    )

    with pytest.raises(AgentBackendError, match="exceeded its budget"):
        await backend.execute(agent, AgentTask(input="say hi"))

import asyncio

from axiom_core.agents.backend import AgentBackendError
from axiom_core.agents.types import Agent, AgentResult, AgentTask
from axiom_core.models import ModelBackend, ModelBackendError, ModelMessage, ModelRequest

_DEFAULT_MAX_TOKENS = 1024

# Real, verified constraint, not a made-up number: the installed
# anthropic SDK (_base_client.py's _calculate_nonstreaming_timeout)
# refuses any non-streaming call above this — it computes
# `3600 * max_tokens / 128_000` and raises ValueError once that exceeds
# 600s, i.e. max_tokens > 21,333.33. AxiomNativeBackend doesn't implement
# streaming, so this is a hard ceiling on what it can honestly enforce.
# Discovered live in Milestone 21 once agent budgets started actually
# being passed through: every one of the 12 curated agents'
# `budget.max_tokens` (25,000-50,000) exceeded it and every delegation
# started failing. Clamped here rather than raised on the curated data,
# since 20,000 output tokens is already far more than any of these demo
# tasks produce — see docs/security/SECURITY_AUDIT.md.
_NONSTREAMING_MAX_TOKENS_CEILING = 20_000


class AxiomNativeBackend:
    """Executes an agent task directly against a configured Model Gateway
    backend, using the agent's instructions as the system prompt. This is
    Axiom's own execution path — CLAUDE.md §30's ``AxiomNativeBackend`` —
    as opposed to routing through Hermes (Milestone 13).

    Enforces ``agent.budget`` for real, not just as descriptive metadata:
    ``max_tokens`` becomes the actual ``ModelRequest.max_tokens`` cap sent
    to the model API (preventive — the model physically can't generate
    more than that, and clamped to
    ``_NONSTREAMING_MAX_TOKENS_CEILING`` since this backend doesn't
    stream), and ``max_seconds`` wraps the model call in
    ``asyncio.wait_for`` (preventive — a real timeout, not a post-hoc
    check). Cancelling an in-flight HTTP call here is safe: there's no
    subprocess to leak, unlike HermesBackend.
    """

    backend_name = "axiom_native"

    def __init__(self, model_backend: ModelBackend, default_model: str) -> None:
        self._model_backend = model_backend
        self._default_model = default_model

    async def is_configured(self) -> bool:
        return await self._model_backend.is_configured()

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        max_tokens = min(
            agent.budget.get("max_tokens", _DEFAULT_MAX_TOKENS), _NONSTREAMING_MAX_TOKENS_CEILING
        )
        request = ModelRequest(
            messages=[ModelMessage(role="user", content=task.input)],
            model=self._default_model,
            max_tokens=max_tokens,
            system=self._build_system_prompt(agent, task),
        )
        max_seconds = agent.budget.get("max_seconds")
        try:
            if max_seconds is not None:
                response = await asyncio.wait_for(self._model_backend.generate(request), timeout=max_seconds)
            else:
                response = await self._model_backend.generate(request)
        except TimeoutError as exc:
            raise AgentBackendError(
                f"Agent {agent.agent_id!r} exceeded its budget: max_seconds={max_seconds}"
            ) from exc
        except ModelBackendError as exc:
            raise AgentBackendError(f"Agent {agent.agent_id!r} execution failed: {exc}") from exc

        return AgentResult(
            content=response.content,
            raw={
                "model": response.model,
                "provider": response.provider,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            },
        )

    @staticmethod
    def _build_system_prompt(agent: Agent, task: AgentTask) -> str:
        parts = [agent.instructions]
        if task.context:
            parts.append(f"Relevant context:\n{task.context}")
        return "\n\n".join(parts)

from axiom_core.agents.backend import AgentBackendError
from axiom_core.agents.types import Agent, AgentResult, AgentTask
from axiom_core.models import ModelBackend, ModelBackendError, ModelMessage, ModelRequest


class AxiomNativeBackend:
    """Executes an agent task directly against a configured Model Gateway
    backend, using the agent's instructions as the system prompt. This is
    Axiom's own execution path — CLAUDE.md §30's ``AxiomNativeBackend`` —
    as opposed to routing through Hermes (Milestone 13).
    """

    backend_name = "axiom_native"

    def __init__(self, model_backend: ModelBackend, default_model: str) -> None:
        self._model_backend = model_backend
        self._default_model = default_model

    async def is_configured(self) -> bool:
        return await self._model_backend.is_configured()

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        request = ModelRequest(
            messages=[ModelMessage(role="user", content=task.input)],
            model=self._default_model,
            system=self._build_system_prompt(agent, task),
        )
        try:
            response = await self._model_backend.generate(request)
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

import os
import shutil

from axiom_core.agents.backend import AgentBackendError
from axiom_core.agents.types import Agent, AgentResult, AgentTask

from axiom_hermes.client import HermesCliError, run_oneshot


class HermesBackend:
    """CLAUDE.md §30's ``HermesBackend`` — a real external agent runtime
    (github.com/NousResearch/hermes-agent), not Axiom's own execution
    path (that's AxiomNativeBackend). Every call shells out to the real,
    installed ``hermes`` CLI's one-shot mode (``hermes -z``) — verified
    live in Milestone 13, including the real gotcha that Hermes's `auto`
    provider detection did not pick Anthropic even with
    ANTHROPIC_API_KEY set, requiring an explicit ``--provider anthropic``.
    """

    backend_name = "hermes"

    def __init__(
        self,
        anthropic_api_key: str,
        *,
        hermes_bin: str = "hermes",
        default_model: str = "anthropic/claude-sonnet-5",
        provider: str = "anthropic",
        timeout: float = 120.0,
    ) -> None:
        self._anthropic_api_key = anthropic_api_key
        self._hermes_bin = hermes_bin
        self._default_model = default_model
        self._provider = provider
        self._timeout = timeout

    async def is_configured(self) -> bool:
        # Local-only check — the `hermes` binary is on PATH. Does not run
        # it (that costs money and latency); see ModelBackend's
        # equivalent is_configured() docstring for the rationale.
        return shutil.which(self._hermes_bin) is not None

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        prompt = self._build_prompt(agent, task)
        env = {**os.environ, "ANTHROPIC_API_KEY": self._anthropic_api_key}

        try:
            result = await run_oneshot(
                self._hermes_bin,
                prompt,
                model=self._default_model,
                provider=self._provider,
                env=env,
                timeout=self._timeout,
            )
        except HermesCliError as exc:
            raise AgentBackendError(f"Agent {agent.agent_id!r} Hermes execution failed: {exc}") from exc

        return AgentResult(content=result.content, raw=result.usage)

    @staticmethod
    def _build_prompt(agent: Agent, task: AgentTask) -> str:
        # hermes -z takes one combined prompt, no separate system channel
        # — same composition AxiomNativeBackend uses for consistency.
        parts = [agent.instructions]
        if task.context:
            parts.append(f"Relevant context:\n{task.context}")
        parts.append(task.input)
        return "\n\n".join(parts)

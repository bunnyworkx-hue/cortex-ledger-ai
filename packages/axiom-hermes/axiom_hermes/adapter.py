import os
import shutil

from axiom_core.agents.backend import AgentBackendError
from axiom_core.agents.types import Agent, AgentResult, AgentTask

from axiom_hermes.client import HermesCliError, HermesTimeoutError, run_oneshot


class HermesBackend:
    """CLAUDE.md §30's ``HermesBackend`` — a real external agent runtime
    (github.com/NousResearch/hermes-agent), not Axiom's own execution
    path (that's AxiomNativeBackend). Every call shells out to the real,
    installed ``hermes`` CLI's one-shot mode (``hermes -z``) — verified
    live in Milestone 13, including the real gotcha that Hermes's `auto`
    provider detection did not pick Anthropic even with
    ANTHROPIC_API_KEY set, requiring an explicit ``--provider anthropic``.

    ``agent.budget["max_seconds"]`` is enforced for real, overriding the
    instance default via ``run_oneshot``'s own safe timeout (which kills
    the subprocess, not just cancels the await). ``max_tokens`` is
    **not** enforced here — Hermes's ``--usage-file`` JSON schema was
    never precisely verified against a live run in this build (only
    "cost, token counts, model, provider, completed/failed" was
    confirmed at a glance), so parsing specific keys to gate on would be
    guessing at an unverified schema (CLAUDE.md §56). Real token-based
    enforcement for Hermes is a named gap, not silently claimed here —
    see docs/security/SECURITY_AUDIT.md.
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
        # agent.budget["max_seconds"], when set, overrides the instance
        # default — enforced by run_oneshot's own wait_for/process.kill()
        # (the safe mechanism it already has for its own timeout), not a
        # generic outer wrapper here that could leave the subprocess
        # running after an outer cancellation.
        timeout = agent.budget.get("max_seconds", self._timeout)

        try:
            result = await run_oneshot(
                self._hermes_bin,
                prompt,
                model=self._default_model,
                provider=self._provider,
                env=env,
                timeout=timeout,
            )
        except HermesTimeoutError as exc:
            raise AgentBackendError(
                f"Agent {agent.agent_id!r} exceeded its budget: max_seconds={timeout}"
            ) from exc
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

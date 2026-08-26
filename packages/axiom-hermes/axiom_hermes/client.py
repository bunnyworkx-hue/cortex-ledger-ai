import asyncio
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path


class HermesCliError(RuntimeError):
    pass


class HermesTimeoutError(HermesCliError):
    pass


@dataclass(frozen=True, slots=True)
class HermesRunResult:
    content: str
    usage: dict


async def run_oneshot(
    hermes_bin: str,
    prompt: str,
    *,
    model: str,
    provider: str,
    env: dict[str, str],
    timeout: float = 120.0,
) -> HermesRunResult:
    """Run a real Hermes Agent one-shot query (``hermes -z``, verified in
    Milestone 13 against the actual installed CLI — see
    docs/hermes/HERMES_INTEGRATION.md). ``-z`` prints only the final
    response text to stdout; ``--usage-file`` writes a real JSON cost/
    token report, written even on failure, which is how failures are
    detected (not just the exit code — verified: a bad provider produces
    exit code 1 *and* a usage file with ``"failed": true`` and a
    ``"failure"`` message).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        usage_path = Path(tmp_dir) / "usage.json"

        process = await asyncio.create_subprocess_exec(
            hermes_bin,
            "-z",
            prompt,
            "-m",
            model,
            "--provider",
            provider,
            "--usage-file",
            str(usage_path),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except TimeoutError as exc:
            process.kill()
            await process.wait()
            raise HermesTimeoutError(f"hermes -z did not finish within {timeout}s") from exc

        usage: dict = {}
        if usage_path.is_file():
            try:
                usage = json.loads(usage_path.read_text())
            except json.JSONDecodeError:
                usage = {}

        if usage.get("failed") or process.returncode != 0:
            failure = usage.get("failure") or stderr.decode(errors="replace").strip() or "unknown error"
            raise HermesCliError(f"hermes -z failed: {failure}")

        return HermesRunResult(content=stdout.decode(errors="replace").strip(), usage=usage)

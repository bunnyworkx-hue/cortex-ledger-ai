import asyncio
import json
from pathlib import Path

import pytest

import axiom_hermes.client as client_module
from axiom_hermes.client import HermesCliError, HermesTimeoutError, run_oneshot


class _FakeProcess:
    def __init__(self, stdout: bytes, stderr: bytes, returncode: int, usage: dict | None, usage_path: Path) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self._usage = usage
        self._usage_path = usage_path
        self.killed = False

    async def communicate(self) -> tuple[bytes, bytes]:
        if self._usage is not None:
            self._usage_path.write_text(json.dumps(self._usage))
        return self._stdout, self._stderr

    def kill(self) -> None:
        self.killed = True

    async def wait(self) -> None:
        return None


def _patch_subprocess(monkeypatch, process_factory):
    async def fake_create_subprocess_exec(*args, **kwargs):
        usage_path = Path(args[args.index("--usage-file") + 1])
        return process_factory(usage_path)

    monkeypatch.setattr(client_module.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)


@pytest.mark.asyncio
async def test_run_oneshot_returns_content_and_usage_on_success(monkeypatch):
    usage = {"completed": True, "failed": False, "model": "claude-sonnet-5", "estimated_cost_usd": 0.01}
    _patch_subprocess(
        monkeypatch,
        lambda usage_path: _FakeProcess(b"Hello!\n", b"", 0, usage, usage_path),
    )

    result = await run_oneshot("hermes", "hi", model="anthropic/claude-sonnet-5", provider="anthropic", env={})

    assert result.content == "Hello!"
    assert result.usage == usage


@pytest.mark.asyncio
async def test_run_oneshot_raises_on_usage_file_failed_flag(monkeypatch):
    usage = {"completed": False, "failed": True, "failure": "No usable credentials found for provider 'gmi'."}
    _patch_subprocess(
        monkeypatch,
        lambda usage_path: _FakeProcess(b"", b"", 1, usage, usage_path),
    )

    with pytest.raises(HermesCliError, match="No usable credentials"):
        await run_oneshot("hermes", "hi", model="anthropic/claude-sonnet-5", provider="anthropic", env={})


@pytest.mark.asyncio
async def test_run_oneshot_raises_on_nonzero_exit_without_usage_file(monkeypatch):
    _patch_subprocess(
        monkeypatch,
        lambda usage_path: _FakeProcess(b"", b"boom", 1, None, usage_path),
    )

    with pytest.raises(HermesCliError, match="boom"):
        await run_oneshot("hermes", "hi", model="anthropic/claude-sonnet-5", provider="anthropic", env={})


@pytest.mark.asyncio
async def test_run_oneshot_raises_timeout_and_kills_process(monkeypatch):
    class _HangingProcess(_FakeProcess):
        async def communicate(self):
            await asyncio.sleep(10)
            return b"", b""

    process_holder: list[_HangingProcess] = []

    def factory(usage_path):
        proc = _HangingProcess(b"", b"", 0, None, usage_path)
        process_holder.append(proc)
        return proc

    _patch_subprocess(monkeypatch, factory)

    with pytest.raises(HermesTimeoutError):
        await run_oneshot(
            "hermes", "hi", model="anthropic/claude-sonnet-5", provider="anthropic", env={}, timeout=0.05
        )

    assert process_holder[0].killed is True

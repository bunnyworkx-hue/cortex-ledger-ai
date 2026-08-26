"""Milestone 20 (Security) — Hermes Security Tests, CLAUDE.md §96.

``HermesBackend`` shells out to a real external CLI (packages/axiom-hermes/
axiom_hermes/client.py). The one property that actually matters for
injection safety is: does a hostile prompt ever reach a shell? It doesn't
— ``run_oneshot`` calls ``asyncio.create_subprocess_exec`` (no ``shell=True``,
no string command line), so the prompt is passed as a single literal argv
element regardless of its contents.

This is proven here against a real subprocess (``/bin/echo`` standing in
for ``hermes`` — no shell in between either way), not asserted from
reading the source: a shell-metacharacter payload comes back byte-for-byte
in stdout, unexpanded, and no side effect occurs.
"""

import os

import pytest

from axiom_hermes.client import run_oneshot

# Classic shell-injection payloads: command chaining, subshell expansion,
# backtick expansion, and a stray unmatched quote (would break a naive
# f"...{prompt}..." shell string, but not an argv list).
_INJECTION_PAYLOADS = [
    "hello; rm -rf /tmp/axiom-injection-marker",
    "hello $(whoami)",
    "hello `id`",
    "hello ' && echo pwned && echo '",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", _INJECTION_PAYLOADS)
async def test_hermes_prompt_is_never_shell_interpreted(payload: str, tmp_path):
    marker = tmp_path / "axiom-injection-marker"
    assert not marker.exists()

    # /bin/echo stands in for the real `hermes` binary: run_oneshot's
    # argv construction is identical regardless of which binary path is
    # given, so this exercises the real subprocess-invocation code path.
    result = await run_oneshot(
        "/bin/echo",
        payload,
        model="unused",
        provider="unused",
        env=dict(os.environ),
    )

    # echo prints its argv back verbatim — if a shell had ever touched
    # this string, `$(whoami)` / backticks would have been expanded and
    # `;`/`&&` would have run a second command instead of being echoed.
    assert payload in result.content
    assert not marker.exists()

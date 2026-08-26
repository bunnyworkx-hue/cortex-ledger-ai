import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

# Directories in agency-agents that are NOT agent divisions — mirrors
# NON_DIVISION_DIRS in the source repo's own scripts/check-divisions.sh
# (verified in docs/agent-fabric/AGENT_LIBRARY_AUDIT.md §4/§6).
_NON_DIVISION_DIRS = {"integrations", "strategy", "examples", "scripts"}


class AgencyAgentsSourceError(RuntimeError):
    """Raised when the agency-agents path doesn't look like the real repo
    (missing divisions.json, not a git repo, ...). Fails loudly rather
    than silently returning an empty registry — CLAUDE.md §57."""


class AgentFileParseError(AgencyAgentsSourceError):
    """Raised when one specific agent file can't be parsed — e.g. a real,
    verified case in the corpus: engineering-developer-tooling-engineer.md
    has an unquoted `description:` containing a bare ": " ("great DX:
    intuitive command design"), which is invalid plain-scalar YAML. This
    is a per-file problem, not a repo-structure problem — callers should
    skip and log rather than fail the whole registry load (see
    normalize.py), per CLAUDE.md §57 ("record limitations")."""


@dataclass(frozen=True, slots=True)
class ParsedAgentFile:
    name: str
    description: str
    body: str
    tools: tuple[str, ...]


def load_divisions(agency_agents_path: Path) -> dict[str, dict]:
    divisions_file = agency_agents_path / "divisions.json"
    if not divisions_file.is_file():
        raise AgencyAgentsSourceError(
            f"{divisions_file} not found — {agency_agents_path} does not look like "
            "a real agency-agents checkout."
        )
    data = json.loads(divisions_file.read_text())
    return data["divisions"]


def get_source_commit(agency_agents_path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=agency_agents_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise AgencyAgentsSourceError(
            f"Could not read the git commit of {agency_agents_path} — is it a real "
            "git checkout?"
        ) from exc
    return result.stdout.strip()


def discover_agent_files(agency_agents_path: Path, divisions: dict[str, dict]) -> list[Path]:
    """Every .md file directly under a real division directory. Mirrors
    the corpus composition verified in AGENT_LIBRARY_AUDIT.md: 255 real
    agent files across these divisions, excluding integrations/strategy/
    examples/scripts (tooling and playbooks, not agents)."""
    files: list[Path] = []
    for division in divisions:
        division_dir = agency_agents_path / division
        if division in _NON_DIVISION_DIRS or not division_dir.is_dir():
            continue
        files.extend(sorted(division_dir.glob("*.md")))
    return files


def parse_agent_file(path: Path) -> ParsedAgentFile:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AgentFileParseError(f"{path} has no YAML frontmatter — not a real agent file.")

    _, frontmatter_raw, body = text.split("---", 2)
    try:
        frontmatter = yaml.safe_load(frontmatter_raw) or {}
    except yaml.YAMLError as exc:
        raise AgentFileParseError(f"{path}: invalid YAML frontmatter — {exc}") from exc

    tools_field = frontmatter.get("tools")
    tools = (
        tuple(t.strip() for t in tools_field.split(",") if t.strip())
        if isinstance(tools_field, str)
        else ()
    )

    return ParsedAgentFile(
        name=frontmatter.get("name", path.stem),
        description=frontmatter.get("description", ""),
        body=body.strip(),
        tools=tools,
    )

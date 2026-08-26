from pathlib import Path

from axiom_core.logging import get_logger

from axiom_agent_fabric.curated import apply_curation
from axiom_agent_fabric.source import (
    AgentFileParseError,
    discover_agent_files,
    get_source_commit,
    load_divisions,
    parse_agent_file,
)
from axiom_agent_fabric.types import AgentRecord

logger = get_logger(__name__)


def normalize_agency_agents(agency_agents_path: Path) -> list[AgentRecord]:
    """The mechanical + curated normalization pipeline
    (IMPLEMENTATION_PLAN.md §2): every real agent file becomes a
    lossless-mechanical AgentRecord, then the small curated cohort
    (axiom_agent_fabric.curated) is layered on top. Never mutates or
    forks the source files themselves — CLAUDE.md §67/§57.

    A single malformed source file (a real, verified case exists — see
    AgentFileParseError's docstring) is skipped and logged rather than
    failing the entire registry load: one bad file in a 255-agent corpus
    must not take down the whole Agent Fabric.
    """
    divisions = load_divisions(agency_agents_path)
    source_commit = get_source_commit(agency_agents_path)

    records: list[AgentRecord] = []
    for path in discover_agent_files(agency_agents_path, divisions):
        division = path.parent.name
        source_path = str(path.relative_to(agency_agents_path))

        try:
            parsed = parse_agent_file(path)
        except AgentFileParseError as exc:
            logger.warning("axiom.agent_fabric.file_skipped", source_path=source_path, error=str(exc))
            continue

        agent_id = source_path.removesuffix(".md")
        record = AgentRecord(
            agent_id=agent_id,
            name=parsed.name,
            description=parsed.description,
            division=division,
            category=divisions[division]["label"],
            instructions=parsed.body,
            source_path=source_path,
            source_commit=source_commit,
            frontmatter_tools=parsed.tools,
        )
        records.append(apply_curation(record))

    return records

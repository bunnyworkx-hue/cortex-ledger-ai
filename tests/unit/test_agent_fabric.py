import json
import subprocess

import pytest

from axiom_agent_fabric.normalize import normalize_agency_agents
from axiom_agent_fabric.registry import AgentNotFoundError, AgentRegistry
from axiom_agent_fabric.source import (
    AgencyAgentsSourceError,
    discover_agent_files,
    load_divisions,
    parse_agent_file,
)
from axiom_agent_fabric.curated import apply_curation
from axiom_agent_fabric.types import AgentRecord, AgentStatus


@pytest.fixture
def fake_agency_agents(tmp_path):
    """A small, real (not mocked) git repo shaped like agency-agents,
    with two divisions and three agents — enough to exercise the whole
    mechanical pipeline without depending on the real 255-agent corpus.
    """
    root = tmp_path / "fake-agency-agents"
    root.mkdir()

    divisions = {
        "divisions": {
            "engineering": {"label": "Engineering", "icon": "Code", "color": "#3B82F6"},
            "marketing": {"label": "Marketing", "icon": "Megaphone", "color": "#F97316"},
        }
    }
    (root / "divisions.json").write_text(json.dumps(divisions))

    (root / "engineering").mkdir()
    (root / "engineering" / "engineering-widget-builder.md").write_text(
        "---\n"
        "name: Widget Builder\n"
        "description: Builds UIs.\n"
        "color: cyan\n"
        "emoji: \U0001f5a5️\n"
        "---\n\n"
        "# Widget Builder Agent Personality\n\nYou build UIs.\n"
    )
    (root / "engineering" / "engineering-backend-architect.md").write_text(
        "---\nname: Backend Architect\ndescription: Designs systems.\ncolor: indigo\nemoji: \U0001f3db️\n---\n\nDesigns backends.\n"
    )
    (root / "marketing").mkdir()
    (root / "marketing" / "marketing-seo-specialist.md").write_text(
        "---\n"
        "name: SEO Specialist\n"
        "description: Optimizes search rankings.\n"
        "tools: WebFetch, WebSearch, Read\n"
        "color: blue\n"
        "emoji: \U0001f50d\n"
        "---\n\nDoes SEO.\n"
    )
    # Non-division dirs must be excluded even if they contain .md files.
    (root / "integrations").mkdir()
    (root / "integrations" / "not-an-agent.md").write_text("---\nname: X\n---\nnope\n")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=test@test.com", "-c", "user.name=test", "commit", "-q", "-m", "init"],
        cwd=root,
        check=True,
    )
    return root


def test_load_divisions_rejects_a_non_agency_agents_path(tmp_path):
    with pytest.raises(AgencyAgentsSourceError):
        load_divisions(tmp_path)


def test_discover_agent_files_excludes_non_division_dirs(fake_agency_agents):
    divisions = load_divisions(fake_agency_agents)
    files = discover_agent_files(fake_agency_agents, divisions)

    names = {f.name for f in files}
    assert names == {
        "engineering-widget-builder.md",
        "engineering-backend-architect.md",
        "marketing-seo-specialist.md",
    }


def test_parse_agent_file_reads_tools_field(fake_agency_agents):
    parsed = parse_agent_file(fake_agency_agents / "marketing" / "marketing-seo-specialist.md")

    assert parsed.name == "SEO Specialist"
    assert parsed.description == "Optimizes search rankings."
    assert parsed.tools == ("WebFetch", "WebSearch", "Read")
    assert "Does SEO." in parsed.body


def test_normalize_produces_mechanical_records_for_every_agent(fake_agency_agents):
    records = normalize_agency_agents(fake_agency_agents)

    assert len(records) == 3
    by_id = {r.agent_id: r for r in records}
    assert "engineering/engineering-widget-builder" in by_id
    assert "marketing/marketing-seo-specialist" in by_id

    frontend = by_id["engineering/engineering-widget-builder"]
    assert frontend.name == "Widget Builder"
    assert frontend.category == "Engineering"
    assert frontend.source_path == "engineering/engineering-widget-builder.md"
    assert len(frontend.source_commit) == 40  # a real git commit sha
    assert frontend.status == AgentStatus.DRAFT  # not in the curated cohort
    assert frontend.capabilities is None


def test_registry_get_list_and_not_found(fake_agency_agents):
    registry = AgentRegistry.load(fake_agency_agents)

    assert len(registry) == 3
    assert registry.get("marketing/marketing-seo-specialist").name == "SEO Specialist"

    with pytest.raises(AgentNotFoundError):
        registry.get("does/not-exist")

    assert len(registry.list(division="engineering")) == 2


def test_registry_search_only_returns_curated_agents(fake_agency_agents):
    # None of the fixture's agent_ids are in the real CURATED_COHORT, so
    # search must return nothing even for an exact name match — proving
    # search v1 really is scoped to curated agents only, not all DRAFT ones.
    registry = AgentRegistry.load(fake_agency_agents)

    assert registry.search("Widget Builder") == []


def test_apply_curation_activates_a_real_curated_agent_id():
    # Deliberately the real agency-agents agent_id (see curated.py's
    # CURATED_COHORT) — this proves curation activates a genuine curated
    # entry, as opposed to the fixture's synthetic "widget-builder" agent
    # above, which must NOT match any curated key.
    mechanical = AgentRecord(
        agent_id="engineering/engineering-frontend-developer",
        name="Frontend Developer",
        description="Expert frontend developer...",
        division="engineering",
        category="Engineering",
        instructions="You are Frontend Developer...",
        source_path="engineering/engineering-frontend-developer.md",
        source_commit="deadbeef" * 5,
    )

    curated = apply_curation(mechanical)

    assert curated.status == AgentStatus.ACTIVE
    assert curated.is_curated is True
    assert "frontend_development" in curated.capabilities
    assert curated.risk_level == "medium"


def test_apply_curation_leaves_uncurated_agents_alone():
    mechanical = AgentRecord(
        agent_id="engineering/engineering-backend-architect",
        name="Backend Architect",
        description="...",
        division="engineering",
        category="Engineering",
        instructions="...",
        source_path="engineering/engineering-backend-architect.md",
        source_commit="deadbeef" * 5,
    )

    assert apply_curation(mechanical) is mechanical

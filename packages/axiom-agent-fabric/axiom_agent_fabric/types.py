from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(str, Enum):
    """CLAUDE.md §69's agent lifecycle. Mechanically-normalized records
    (no curated capability data) start DRAFT; the curated cohort starts
    ACTIVE. Nothing here auto-promotes a DRAFT agent to ACTIVE — that's a
    deliberate human decision per CLAUDE.md §69 ("do not allow untested
    agents to automatically perform high-risk production actions")."""

    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    PAUSED = "paused"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass(frozen=True, slots=True)
class AgentRecord:
    """A normalized Cortex Ledger AI Agent Fabric record. Two provenances feed this:

    - Mechanical (all ~255 agents): agent_id/name/description/category/
      division/instructions/source_path/source_commit/frontmatter_tools —
      a lossless transform of the real agency-agents source, always
      present.
    - Curated (a small first cohort, CLAUDE.md's own instruction not to
      auto-infer capabilities from prose for all 255 on day one):
      capabilities/permissions/risk_level/budget — None until a human
      curates them; presence of these is what the Router (v1, explicit
      routing only) actually searches over.
    """

    agent_id: str
    name: str
    description: str
    division: str
    category: str
    instructions: str
    source_path: str
    source_commit: str
    frontmatter_tools: tuple[str, ...] = ()

    status: AgentStatus = AgentStatus.DRAFT
    capabilities: tuple[str, ...] | None = None
    permissions: tuple[str, ...] | None = None
    risk_level: str | None = None
    budget: dict = field(default_factory=dict)

    @property
    def is_curated(self) -> bool:
        return self.capabilities is not None

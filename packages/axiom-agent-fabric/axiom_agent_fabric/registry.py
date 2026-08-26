from pathlib import Path

from axiom_agent_fabric.normalize import normalize_agency_agents
from axiom_agent_fabric.types import AgentRecord, AgentStatus


class AgentNotFoundError(KeyError):
    pass


class AgentRegistry:
    """The Agent Fabric's source of truth (CLAUDE.md §8), built once from
    a real agency-agents checkout and held in memory. DB-backed
    persistence (the `agents` table from CLAUDE.md §48) is a later
    milestone — this is the MVP registry CLAUDE.md §66 asks for:
    Create/Register/Get/List/Search/Filter-by-capability, backed by a
    real import instead of hand-recreated records.
    """

    def __init__(self, records: list[AgentRecord]) -> None:
        self._records: dict[str, AgentRecord] = {r.agent_id: r for r in records}

    @classmethod
    def load(cls, agency_agents_path: Path) -> "AgentRegistry":
        return cls(normalize_agency_agents(agency_agents_path))

    def get(self, agent_id: str) -> AgentRecord:
        try:
            return self._records[agent_id]
        except KeyError as exc:
            raise AgentNotFoundError(f"No agent registered with id {agent_id!r}") from exc

    def list(
        self, *, division: str | None = None, status: AgentStatus | None = None
    ) -> list[AgentRecord]:
        records = self._records.values()
        if division is not None:
            records = (r for r in records if r.division == division)
        if status is not None:
            records = (r for r in records if r.status == status)
        return sorted(records, key=lambda r: r.agent_id)

    def search(self, query: str, *, division: str | None = None, limit: int = 10) -> list[AgentRecord]:
        """Explicit routing v1 (CLAUDE.md §10: "do not jump directly to
        Version 4") — keyword matching over the curated cohort only.
        Uncurated (DRAFT) records have no capability tags to search over
        yet, so including them would just be a name/description grep,
        not real capability-based discovery; excluding them keeps search
        results meaningfully scoped until more agents are curated.
        """
        terms = [t.lower() for t in query.split() if t]
        if not terms:
            return []

        scored: list[tuple[int, AgentRecord]] = []
        for record in self._records.values():
            if not record.is_curated:
                continue
            if division is not None and record.division != division:
                continue
            haystack = " ".join(
                [record.name, record.description, *(record.capabilities or ())]
            ).lower()
            score = sum(haystack.count(term) for term in terms)
            if score > 0:
                scored.append((score, record))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [record for _, record in scored[:limit]]

    def __len__(self) -> int:
        return len(self._records)

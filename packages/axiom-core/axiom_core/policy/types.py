import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class PolicyStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    status: PolicyStatus
    reason: str


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class ApprovalRequest:
    """CLAUDE.md §37's human approval workflow, stored so a pending
    action survives past the request that proposed it — a human approves
    or rejects it later, out of band, via /v1/approvals.
    """

    id: str
    action: str
    risk_level: str
    reason: str
    payload: dict
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None
    decided_by: str | None = None

    @staticmethod
    def new(*, action: str, risk_level: str, reason: str, payload: dict) -> "ApprovalRequest":
        return ApprovalRequest(
            id=str(uuid.uuid4()), action=action, risk_level=risk_level, reason=reason, payload=payload
        )

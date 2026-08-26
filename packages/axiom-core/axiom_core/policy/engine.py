from axiom_core.policy.types import PolicyDecision, PolicyStatus

# CLAUDE.md §36's risk levels, in ascending order.
_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class PolicyEngine:
    """CLAUDE.md §35: "the model is not the authority... the Policy
    Engine is the authority." Version 1 (CLAUDE.md §37's own guidance
    not to jump straight to a sophisticated version): a single risk
    threshold. low/medium risk actions are allowed; high/critical
    require human approval. Nothing is auto-denied outright yet — denial
    is Milestone 15's future work once there's a real reason to deny
    (e.g. a budget actually exhausted) rather than a threshold to invent.
    """

    def __init__(self, *, approval_threshold: str = "high") -> None:
        self._approval_threshold = _RISK_ORDER.get(approval_threshold, _RISK_ORDER["high"])

    def evaluate(self, risk_level: str, *, action: str) -> PolicyDecision:
        level = _RISK_ORDER.get(risk_level, _RISK_ORDER["medium"])
        if level >= self._approval_threshold:
            return PolicyDecision(
                status=PolicyStatus.REQUIRES_APPROVAL,
                reason=f"{action!r} is risk_level={risk_level!r}, at or above the "
                f"approval threshold — a human must approve it via /v1/approvals.",
            )
        return PolicyDecision(status=PolicyStatus.ALLOW, reason=f"risk_level={risk_level!r} is auto-allowed")

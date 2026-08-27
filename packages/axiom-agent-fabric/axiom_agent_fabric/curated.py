"""The first curated Agent Fabric cohort — 12 real agents spanning 10
divisions, hand-picked and hand-tagged per IMPLEMENTATION_PLAN.md §2
("populated by hand for a small first cohort ... not auto-inferred from
prose for all 255 on day one"). Every entry below is grounded in that
agent's real frontmatter `description` (see docs/agent-fabric/
AGENT_LIBRARY_AUDIT.md) — capabilities/permissions/risk_level are Cortex Ledger AI's
own categorization of real, described capabilities, not invented ones
(CLAUDE.md §56 forbids fabricating capabilities, not tagging real ones).

Risk levels follow the CLAUDE.md §36 examples: read-only/advisory work is
LOW, work that writes code/content/customer-facing state is MEDIUM;
nothing in this first cohort reaches HIGH/CRITICAL (payments, deletions,
production deploys) — those risk levels are reserved for agents/tools not
yet in scope.
"""

import dataclasses

from axiom_agent_fabric.types import AgentRecord, AgentStatus

CuratedEntry = dict


CURATED_COHORT: dict[str, CuratedEntry] = {
    "engineering/engineering-frontend-developer": {
        "capabilities": ("frontend_development", "react_vue_angular", "performance_optimization", "accessibility"),
        "permissions": ("code.read", "code.write"),
        "risk_level": "medium",
        "budget": {"max_tokens": 40000, "max_seconds": 240},
    },
    "engineering/engineering-software-architect": {
        "capabilities": ("system_design", "domain_driven_design", "architecture_review"),
        "permissions": ("code.read", "architecture.read"),
        "risk_level": "low",
        "budget": {"max_tokens": 50000, "max_seconds": 300},
    },
    "security/security-appsec-engineer": {
        "capabilities": ("threat_modeling", "secure_code_review", "sast_dast_integration"),
        "permissions": ("code.read", "security.read"),
        "risk_level": "medium",
        "budget": {"max_tokens": 40000, "max_seconds": 240},
    },
    "sales/sales-deal-strategist": {
        "capabilities": ("meddpicc_qualification", "competitive_positioning", "win_planning"),
        "permissions": ("crm.read",),
        "risk_level": "low",
        "budget": {"max_tokens": 30000, "max_seconds": 180},
    },
    "product/product-manager": {
        "capabilities": ("product_strategy", "roadmap_planning", "stakeholder_alignment"),
        "permissions": ("product.read", "product.write"),
        "risk_level": "medium",
        "budget": {"max_tokens": 40000, "max_seconds": 240},
    },
    "testing/testing-test-automation-engineer": {
        "capabilities": ("test_automation", "playwright_cypress", "ci_parallelization"),
        "permissions": ("code.read", "code.write", "ci.write"),
        "risk_level": "medium",
        "budget": {"max_tokens": 35000, "max_seconds": 240},
    },
    "project-management/project-management-project-shepherd": {
        "capabilities": ("project_coordination", "timeline_management", "stakeholder_alignment"),
        "permissions": ("project.read", "project.write"),
        "risk_level": "low",
        "budget": {"max_tokens": 30000, "max_seconds": 180},
    },
    "support/support-support-responder": {
        "capabilities": ("customer_support", "issue_resolution", "multichannel_support"),
        "permissions": ("support.read", "support.write"),
        "risk_level": "medium",
        "budget": {"max_tokens": 25000, "max_seconds": 150},
    },
    "marketing/marketing-seo-specialist": {
        "capabilities": ("technical_seo", "content_optimization", "link_authority_building"),
        "permissions": ("web.search", "content.write"),
        "risk_level": "low",
        "budget": {"max_tokens": 35000, "max_seconds": 240},
    },
    "design/design-ux-architect": {
        "capabilities": ("ux_architecture", "css_systems", "implementation_guidance"),
        "permissions": ("design.read", "code.read"),
        "risk_level": "low",
        "budget": {"max_tokens": 30000, "max_seconds": 180},
    },
    "finance/finance-fpa-analyst": {
        "capabilities": ("budgeting", "variance_analysis", "financial_forecasting"),
        "permissions": ("finance.read",),
        "risk_level": "medium",
        "budget": {"max_tokens": 35000, "max_seconds": 240},
    },
    "gis/gis-spatial-data-scientist": {
        "capabilities": ("spatial_analytics", "spatial_econometrics", "predictive_modeling"),
        "permissions": ("data.read",),
        "risk_level": "low",
        "budget": {"max_tokens": 35000, "max_seconds": 240},
    },
}


def apply_curation(record: AgentRecord) -> AgentRecord:
    entry = CURATED_COHORT.get(record.agent_id)
    if entry is None:
        return record
    return dataclasses.replace(
        record,
        status=AgentStatus.ACTIVE,
        capabilities=entry["capabilities"],
        permissions=entry["permissions"],
        risk_level=entry["risk_level"],
        budget=entry["budget"],
    )

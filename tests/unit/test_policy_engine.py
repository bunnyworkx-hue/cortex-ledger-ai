from axiom_core.policy import PolicyEngine, PolicyStatus


def test_low_and_medium_risk_are_allowed():
    engine = PolicyEngine(approval_threshold="high")

    assert engine.evaluate("low", action="test").status == PolicyStatus.ALLOW
    assert engine.evaluate("medium", action="test").status == PolicyStatus.ALLOW


def test_high_and_critical_risk_require_approval():
    engine = PolicyEngine(approval_threshold="high")

    high = engine.evaluate("high", action="modify_business_record")
    assert high.status == PolicyStatus.REQUIRES_APPROVAL
    assert "modify_business_record" in high.reason

    assert engine.evaluate("critical", action="test").status == PolicyStatus.REQUIRES_APPROVAL


def test_unknown_risk_level_defaults_to_medium_and_is_allowed():
    engine = PolicyEngine(approval_threshold="high")

    assert engine.evaluate("not-a-real-level", action="test").status == PolicyStatus.ALLOW


def test_threshold_is_configurable():
    strict_engine = PolicyEngine(approval_threshold="medium")

    assert strict_engine.evaluate("medium", action="test").status == PolicyStatus.REQUIRES_APPROVAL
    assert strict_engine.evaluate("low", action="test").status == PolicyStatus.ALLOW

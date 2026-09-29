from app.models import RiskLevel
from app.schemas import AgentDecision
from app.services.policy import evaluate_policy


def test_low_risk_allowlisted_tool_is_auto_approved() -> None:
    decision = AgentDecision(
        category="asset_lookup",
        risk_level=RiskLevel.LOW,
        proposed_tool="lookup_asset",
        tool_arguments={"query": "Laptop 42"},
        rationale="Read only.",
        confidence=0.9,
    )
    assert evaluate_policy(decision).requires_approval is False


def test_high_risk_action_requires_approval() -> None:
    decision = AgentDecision(
        category="access_change",
        risk_level=RiskLevel.HIGH,
        proposed_tool="disable_user_access",
        tool_arguments={"user": "demo"},
        rationale="Destructive.",
        confidence=0.9,
    )
    assert evaluate_policy(decision).requires_approval is True

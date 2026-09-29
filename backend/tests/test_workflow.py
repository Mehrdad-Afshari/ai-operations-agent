from app.models import RiskLevel
from app.schemas import AgentDecision
from app.services.agent import AgentProvider
from app.services.workflow import run_workflow


class StubProvider(AgentProvider):
    def __init__(self, decision: AgentDecision) -> None:
        self.decision = decision

    def decide(self, title: str, description: str) -> AgentDecision:
        return self.decision


def test_workflow_executes_allowlisted_low_risk_tool() -> None:
    provider = StubProvider(
        AgentDecision(
            category="asset_lookup",
            risk_level=RiskLevel.LOW,
            proposed_tool="lookup_asset",
            tool_arguments={"query": "Laptop 42"},
            rationale="Read only.",
            confidence=0.95,
        )
    )

    state = run_workflow("Laptop status", "Find Laptop 42", provider)

    assert state["requires_approval"] is False
    assert state["tool_result"]["status"] == "ok"


def test_workflow_stops_before_high_risk_tool_execution() -> None:
    provider = StubProvider(
        AgentDecision(
            category="access_change",
            risk_level=RiskLevel.HIGH,
            proposed_tool="disable_user_access",
            tool_arguments={"reason": "Contractor departed"},
            rationale="Destructive action.",
            confidence=0.95,
        )
    )

    state = run_workflow("Disable account", "Disable contractor access", provider)

    assert state["requires_approval"] is True
    assert "tool_result" not in state

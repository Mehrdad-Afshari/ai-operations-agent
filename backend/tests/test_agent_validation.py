import pytest

from app.models import RiskLevel
from app.schemas import AgentDecision
from app.services.agent import validate_decision


def test_agent_decision_rejects_unknown_tool() -> None:
    decision = AgentDecision(
        category="unknown",
        risk_level=RiskLevel.LOW,
        proposed_tool="run_shell_command",
        tool_arguments={"command": "whoami"},
        rationale="Invalid tool selection.",
        confidence=0.8,
    )

    with pytest.raises(ValueError, match="non-allow-listed tool"):
        validate_decision(decision)

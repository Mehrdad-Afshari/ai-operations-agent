from dataclasses import dataclass

from app.models import RiskLevel
from app.schemas import AgentDecision


@dataclass(frozen=True)
class PolicyResult:
    requires_approval: bool
    reason: str


AUTO_APPROVED_TOOLS = {"lookup_asset", "create_internal_note"}


def evaluate_policy(decision: AgentDecision) -> PolicyResult:
    if decision.risk_level is RiskLevel.HIGH:
        return PolicyResult(True, "High-risk actions always require human approval.")

    if decision.proposed_tool not in AUTO_APPROVED_TOOLS:
        return PolicyResult(
            True,
            "Tool has side effects or is not in the auto-approval allow-list.",
        )

    return PolicyResult(
        False,
        "Low/medium-risk read-only or internal-note action is allow-listed.",
    )

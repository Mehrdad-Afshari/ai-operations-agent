from app.models import RiskLevel
from app.schemas import AgentDecision


def make_deterministic_decision(title: str, description: str) -> AgentDecision:
    text = f"{title} {description}".lower()

    if any(word in text for word in ("delete", "disable", "revoke", "terminate")):
        return AgentDecision(
            category="access_change",
            risk_level=RiskLevel.HIGH,
            proposed_tool="disable_user_access",
            tool_arguments={"reason": description},
            rationale="Potentially destructive access-management request.",
            confidence=0.90,
        )

    if any(word in text for word in ("asset", "laptop", "device")):
        return AgentDecision(
            category="asset_lookup",
            risk_level=RiskLevel.LOW,
            proposed_tool="lookup_asset",
            tool_arguments={"query": description},
            rationale="Read-only asset information request.",
            confidence=0.85,
        )

    return AgentDecision(
        category="general_operations",
        risk_level=RiskLevel.MEDIUM,
        proposed_tool="create_internal_note",
        tool_arguments={"content": description},
        rationale="General request routed to an internal-note workflow.",
        confidence=0.70,
    )

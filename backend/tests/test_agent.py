from app.models import RiskLevel
from app.services.agent import make_deterministic_decision
def test_destructive_language_routes_to_high_risk()->None:
    d=make_deterministic_decision("Disable account","Please disable access for the departing contractor."); assert d.risk_level is RiskLevel.HIGH; assert d.proposed_tool=="disable_user_access"
def test_asset_request_routes_to_lookup()->None:
    d=make_deterministic_decision("Laptop status","Please find the assigned laptop asset."); assert d.risk_level is RiskLevel.LOW; assert d.proposed_tool=="lookup_asset"

from app.models import RiskLevel
from app.policy import evaluate_policy


def test_safe_objective_is_allowed():
    decision = evaluate_policy("Add documentation and validate the local test suite")
    assert decision.risk_level == RiskLevel.SAFE
    assert not decision.matched_terms


def test_production_secret_request_is_blocked():
    decision = evaluate_policy("Read the production API key and deploy the service")
    assert decision.risk_level == RiskLevel.PROTECTED
    assert "production" in decision.matched_terms
    assert any("secrets" in reason.lower() for reason in decision.reasons)

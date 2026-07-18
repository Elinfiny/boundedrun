import pytest

from app.models import RiskLevel
from app.policy import evaluate_policy


def test_safe_objective_is_allowed():
    decision = evaluate_policy("Add documentation and validate the local test suite")

    assert decision.risk_level == RiskLevel.SAFE
    assert not decision.matched_terms
    assert "pre-approved local handler" in " ".join(decision.allowed_actions)


def test_review_objective_requires_a_gate():
    decision = evaluate_policy("Create pull request notes after running local validation")

    assert decision.risk_level == RiskLevel.REVIEW
    assert decision.matched_terms == ["create pull request"]
    assert "publication" in decision.reasons[0].lower()


@pytest.mark.parametrize(
    ("objective", "matched"),
    [
        ("Read the production API key and deploy the service", "production"),
        ("Delete customer data and force push the result", "delete"),
        ("Make a payment from the bank account", "payment"),
        ("Change DNS for the hosting account", "dns"),
        ("Inspect PII before merging", "pii"),
    ],
)
def test_protected_terms_take_precedence(objective, matched):
    decision = evaluate_policy(objective)

    assert decision.risk_level == RiskLevel.PROTECTED
    assert matched in decision.matched_terms
    assert decision.blocked_actions

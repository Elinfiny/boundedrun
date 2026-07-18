from types import SimpleNamespace

import openai
import pytest

from app.models import ExecutionPlan, Handler, PlanStep, RiskLevel
from app.planner import AI_MODEL, ai_plan, create_plan, deterministic_plan
from app.policy import evaluate_policy


def sample_plan(handler: Handler = Handler.DOCUMENTATION_UPDATE) -> ExecutionPlan:
    return ExecutionPlan(
        summary="Produce a bounded repository-scoped documentation package.",
        handler=handler,
        steps=[PlanStep(order=1, action="Draft the package", evidence="Markdown artifact")],
        validation_gates=["Artifact contract passes"],
        protected_boundaries=["No external mutation"],
    )


class FakeResponses:
    def __init__(self, output_parsed, captured):
        self.output_parsed = output_parsed
        self.captured = captured

    def parse(self, **kwargs):
        self.captured.update(kwargs)
        return SimpleNamespace(output_parsed=self.output_parsed)


def install_fake_client(monkeypatch, output_parsed, captured):
    responses = FakeResponses(output_parsed, captured)
    monkeypatch.setattr(openai, "OpenAI", lambda: SimpleNamespace(responses=responses))


@pytest.mark.parametrize(
    ("objective", "handler"),
    [
        ("Document the bounded policy workflow.", Handler.DOCUMENTATION_UPDATE),
        ("Review the local JSON configuration.", Handler.CONFIGURATION_REVIEW),
        ("Validate the bounded test behavior.", Handler.TEST_VALIDATION),
    ],
)
def test_deterministic_plan_selects_each_allowlisted_handler(objective, handler):
    plan = deterministic_plan(objective, evaluate_policy(objective))

    assert plan.handler == handler
    assert [step.order for step in plan.steps] == [1, 2, 3, 4]


def test_deterministic_plan_blocks_protected_objective():
    objective = "Delete the production database."
    decision = evaluate_policy(objective)

    plan = deterministic_plan(objective, decision)

    assert decision.risk_level == RiskLevel.PROTECTED
    assert plan.handler == Handler.NONE
    assert "unexecuted" in plan.validation_gates[0]


def test_ai_plan_uses_gpt_5_6_and_pydantic_contract(monkeypatch):
    captured = {}
    expected = sample_plan()
    install_fake_client(monkeypatch, expected, captured)
    decision = evaluate_policy("Document the bounded workflow.")

    plan = ai_plan("Document the bounded workflow.", decision)

    assert plan == expected
    assert captured["model"] == AI_MODEL == "gpt-5.6"
    assert captured["text_format"] is ExecutionPlan
    assert captured["input"][0]["role"] == "system"


def test_successful_ai_plan_records_provenance(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    captured = {}
    install_fake_client(monkeypatch, sample_plan(), captured)
    objective = "Document the bounded workflow."

    plan, provenance = create_plan(objective, evaluate_policy(objective), use_ai=True)

    assert plan.handler == Handler.DOCUMENTATION_UPDATE
    assert provenance.source == "openai_responses"
    assert provenance.fallback_used is False
    assert provenance.ai_attempted is True


@pytest.mark.parametrize(
    "bad_output",
    [
        None,
        {"summary": "Missing required plan fields"},
        sample_plan(handler=Handler.NONE),
    ],
)
def test_malformed_or_policy_inconsistent_ai_output_uses_visible_fallback(
    monkeypatch, bad_output
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    install_fake_client(monkeypatch, bad_output, {})
    objective = "Document the bounded workflow."

    plan, provenance = create_plan(objective, evaluate_policy(objective), use_ai=True)

    assert plan.handler == Handler.DOCUMENTATION_UPDATE
    assert provenance.fallback_used is True
    assert provenance.ai_attempted is True
    assert "fallback used" in provenance.detail


def test_protected_ai_output_cannot_select_an_executable_handler(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    install_fake_client(monkeypatch, sample_plan(), {})
    objective = "Delete the production database."

    plan, provenance = create_plan(objective, evaluate_policy(objective), use_ai=True)

    assert plan.handler == Handler.NONE
    assert provenance.fallback_used is True


def test_deterministic_selection_and_missing_key_are_distinguishable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    objective = "Validate the bounded local package."
    decision = evaluate_policy(objective)

    _, selected = create_plan(objective, decision, use_ai=False)
    _, fallback = create_plan(objective, decision, use_ai=True)

    assert selected.fallback_used is False
    assert selected.ai_requested is False
    assert fallback.fallback_used is True
    assert fallback.ai_attempted is False
    assert "not configured" in fallback.detail

import json
from hashlib import sha256

import pytest

from app.executor import execute_bounded
from app.models import ExecutionPlan, Handler, PlanStep
from app.policy import evaluate_policy


def plan_for(handler: Handler) -> ExecutionPlan:
    return ExecutionPlan(
        summary="Execute one bounded allow-listed local handler safely.",
        handler=handler,
        steps=[PlanStep(order=1, action="Execute bounded handler", evidence="Artifact")],
        validation_gates=["Artifact contract passes"],
        protected_boundaries=["No external mutation"],
    )


@pytest.mark.parametrize(
    ("handler", "objective"),
    [
        (Handler.DOCUMENTATION_UPDATE, "Document the bounded contribution workflow."),
        (Handler.CONFIGURATION_REVIEW, "Review the local JSON configuration safely."),
        (Handler.TEST_VALIDATION, "Validate the local bounded test package."),
    ],
)
def test_each_allowlisted_handler_produces_validated_hashed_artifact(handler, objective):
    validations, artifact = execute_bounded(
        objective,
        evaluate_policy(objective),
        plan_for(handler),
    )

    assert artifact
    assert all(item.passed for item in validations)
    digest = sha256(artifact.encode()).hexdigest()
    assert validations[2].detail == f"SHA-256: {digest}"
    if handler == Handler.CONFIGURATION_REVIEW:
        assert json.loads(artifact)["network_access"] is False


def test_protected_policy_and_none_handler_stop_before_execution():
    protected = "Delete the production database."
    validations, artifact = execute_bounded(
        protected,
        evaluate_policy(protected),
        plan_for(Handler.TEST_VALIDATION),
    )
    none_validations, none_artifact = execute_bounded(
        "Validate the bounded package.",
        evaluate_policy("Validate the bounded package."),
        plan_for(Handler.NONE),
    )

    assert validations[0].name == "protected_boundary"
    assert artifact is None
    assert none_validations[0].passed is True
    assert none_artifact is None


def test_handler_not_in_runtime_allowlist_fails(monkeypatch):
    objective = "Document the bounded package."
    monkeypatch.setattr("app.executor.ALLOWED_HANDLERS", set())

    validations, artifact = execute_bounded(
        objective,
        evaluate_policy(objective),
        plan_for(Handler.DOCUMENTATION_UPDATE),
    )

    assert validations[0].name == "handler_allowlist"
    assert validations[0].passed is False
    assert artifact is None


def test_test_handler_reports_contract_failure_for_too_short_direct_input():
    validations, artifact = execute_bounded(
        "tiny",
        evaluate_policy("tiny"),
        plan_for(Handler.TEST_VALIDATION),
    )

    assert artifact
    assert validations[1].name == "artifact_contract"
    assert validations[1].passed is False

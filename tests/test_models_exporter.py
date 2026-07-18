import pytest
from pydantic import ValidationError

from app.exporter import build_work_package, render_markdown
from app.models import ExecutionPlan, Handler, PlanStep, RunRequest
from app.service import run_objective
from app.store import initialize


def test_run_request_normalizes_whitespace_and_revalidates_length():
    request = RunRequest(objective="  Validate   bounded   work.  ")

    assert request.objective == "Validate bounded work."
    with pytest.raises(ValidationError):
        RunRequest(objective="   tiny   ")
    with pytest.raises(ValidationError):
        RunRequest(objective=42)


def test_execution_plan_forbids_extra_fields_and_out_of_order_steps():
    payload = {
        "summary": "Create a bounded work package with ordered steps.",
        "handler": "documentation_update",
        "steps": [{"order": 2, "action": "Draft package", "evidence": "Artifact"}],
        "validation_gates": ["Contract passes"],
        "protected_boundaries": ["No production access"],
    }

    with pytest.raises(ValidationError, match="contiguous order"):
        ExecutionPlan.model_validate(payload)
    payload["steps"][0]["order"] = 1
    payload["unexpected"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        ExecutionPlan.model_validate(payload)
    assert ExecutionPlan.model_json_schema()["additionalProperties"] is False


def test_work_package_contains_complete_bounded_instructions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    initialize()
    receipt = run_objective(
        RunRequest(objective="Document the bounded repository workflow.", use_ai=False)
    )

    package = build_work_package(receipt)
    markdown = render_markdown(package)

    assert package.normalized_objective == receipt.objective
    assert package.implementation_steps == receipt.plan.steps
    assert package.validation_gates
    assert package.protected_boundaries
    assert package.evidence_requirements
    assert any("AGENTS.md" in item for item in package.repository_instructions)
    assert receipt.artifact_sha256 in markdown
    assert "### Allowed actions" in markdown


@pytest.mark.parametrize("planner", ["gpt-5.6", "deterministic"])
def test_legacy_receipt_gets_export_provenance(tmp_path, monkeypatch, planner):
    monkeypatch.chdir(tmp_path)
    initialize()
    receipt = run_objective(
        RunRequest(objective="Document the bounded repository workflow.", use_ai=False)
    ).model_copy(update={"planner": planner, "planner_provenance": None})

    package = build_work_package(receipt)

    assert "predates detailed" in package.planner_provenance.detail
    if planner == "gpt-5.6":
        assert package.planner_provenance.source == "openai_responses"
    else:
        assert package.planner_provenance.source == "deterministic"


def test_plan_step_contract_rejects_extra_fields():
    with pytest.raises(ValidationError):
        PlanStep.model_validate(
            {"order": 1, "action": "Bounded action", "evidence": "Receipt", "shell": "no"}
        )
    assert Handler.NONE.value == "none"

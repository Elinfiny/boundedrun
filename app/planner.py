from __future__ import annotations

import json
import os
from typing import Any

from app.models import ExecutionPlan, Handler, PlanStep, PolicyDecision, RiskLevel

SYSTEM_PROMPT = """
You are the planning component of BoundedRun, a governed execution system.
Return JSON only with these keys: summary, handler, steps, validation_gates,
protected_boundaries. handler must be one of documentation_update,
configuration_review, test_validation, none. Use only the smallest safe handler.
Never authorize secrets, production deployment, financial actions, destructive
changes, personal data access, force-push, or external account mutation.
Each step must contain order, action, and evidence.
""".strip()


def _select_handler(objective: str) -> Handler:
    lowered = objective.lower()
    if any(term in lowered for term in ("document", "readme", "guide", "policy")):
        return Handler.DOCUMENTATION_UPDATE
    if any(term in lowered for term in ("config", "configuration", "json", "schema")):
        return Handler.CONFIGURATION_REVIEW
    return Handler.TEST_VALIDATION


def deterministic_plan(objective: str, decision: PolicyDecision) -> ExecutionPlan:
    if decision.risk_level == RiskLevel.PROTECTED:
        return ExecutionPlan(
            summary="The objective reaches a protected boundary and is intentionally blocked.",
            handler=Handler.NONE,
            steps=[
                PlanStep(
                    order=1,
                    action="Inspect and classify the objective",
                    evidence="Policy decision",
                ),
                PlanStep(
                    order=2,
                    action="Stop before protected execution",
                    evidence="Blocked receipt",
                ),
            ],
            validation_gates=["Protected action remains unexecuted"],
            protected_boundaries=decision.blocked_actions,
        )

    handler = _select_handler(objective)
    return ExecutionPlan(
        summary=(
            "Create a bounded work package, run one approved local handler, "
            "and validate evidence."
        ),
        handler=handler,
        steps=[
            PlanStep(order=1, action="Normalize the objective", evidence="Structured work package"),
            PlanStep(
                order=2,
                action=f"Run approved handler: {handler.value}",
                evidence="Generated artifact",
            ),
            PlanStep(order=3, action="Execute validation gates", evidence="Validation results"),
            PlanStep(order=4, action="Issue an immutable-style receipt", evidence="Run receipt"),
        ],
        validation_gates=[
            "Handler is explicitly allow-listed",
            "No protected term is executed",
            "Required evidence is present",
            "All deterministic checks pass",
        ],
        protected_boundaries=[
            "No secrets or credentials",
            "No production deployment",
            "No financial or destructive action",
            "No private project data",
        ],
    )


def _extract_json(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Planner response did not contain a JSON object")
    return json.loads(text[start : end + 1])


def ai_plan(objective: str, decision: PolicyDecision) -> ExecutionPlan:
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
        instructions=SYSTEM_PROMPT,
        input=json.dumps(
            {
                "objective": objective,
                "policy_decision": decision.model_dump(mode="json"),
            }
        ),
    )
    return ExecutionPlan.model_validate(_extract_json(response.output_text))


def create_plan(
    objective: str, decision: PolicyDecision, use_ai: bool
) -> tuple[ExecutionPlan, str]:
    if use_ai and os.getenv("OPENAI_API_KEY"):
        try:
            return ai_plan(objective, decision), "gpt-5.6"
        except Exception:
            # The demo remains functional and auditable even when the network/model is unavailable.
            pass
    return deterministic_plan(objective, decision), "deterministic"

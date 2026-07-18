from __future__ import annotations

import json
import os

from app.models import (
    ExecutionPlan,
    Handler,
    PlannerProvenance,
    PlanStep,
    PolicyDecision,
    RiskLevel,
)

AI_MODEL = "gpt-5.6"

SYSTEM_PROMPT = """
You are the planning component of BoundedRun, a governed execution system.
Follow the supplied ExecutionPlan schema exactly. Use only the smallest safe handler.
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


def ai_plan(objective: str, decision: PolicyDecision) -> ExecutionPlan:
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.parse(
        model=AI_MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Create a bounded execution plan for this input:\n"
                    + json.dumps(
                        {
                            "objective": objective,
                            "policy_decision": decision.model_dump(mode="json"),
                        }
                    )
                ),
            },
        ],
        text_format=ExecutionPlan,
    )
    if response.output_parsed is None:
        raise ValueError("Planner response did not contain a parsed execution plan")
    plan = ExecutionPlan.model_validate(response.output_parsed)
    if decision.risk_level == RiskLevel.PROTECTED and plan.handler != Handler.NONE:
        raise ValueError("Protected objectives must use the none handler")
    if decision.risk_level != RiskLevel.PROTECTED and plan.handler == Handler.NONE:
        raise ValueError("Non-protected objectives require an allow-listed handler")
    return plan


def create_plan(
    objective: str, decision: PolicyDecision, use_ai: bool
) -> tuple[ExecutionPlan, PlannerProvenance]:
    if use_ai and os.getenv("OPENAI_API_KEY"):
        try:
            return ai_plan(objective, decision), PlannerProvenance(
                source="openai_responses",
                model=AI_MODEL,
                ai_requested=True,
                ai_attempted=True,
                fallback_used=False,
                detail="Strict Responses API output validated into ExecutionPlan.",
            )
        except Exception as error:
            return deterministic_plan(objective, decision), PlannerProvenance(
                source="deterministic",
                model="deterministic",
                ai_requested=True,
                ai_attempted=True,
                fallback_used=True,
                detail=(
                    "GPT-5.6 planning failed; deterministic fallback used "
                    f"({type(error).__name__})."
                ),
            )

    if use_ai:
        detail = "OPENAI_API_KEY is not configured; deterministic fallback used."
        fallback_used = True
    else:
        detail = "Deterministic planning was selected for this run."
        fallback_used = False
    return deterministic_plan(objective, decision), PlannerProvenance(
        source="deterministic",
        model="deterministic",
        ai_requested=use_ai,
        ai_attempted=False,
        fallback_used=fallback_used,
        detail=detail,
    )

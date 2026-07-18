from __future__ import annotations

from app.executor import execute_bounded
from app.models import RiskLevel, RunReceipt, RunRequest, RunStatus
from app.planner import create_plan
from app.policy import evaluate_policy
from app.store import save_receipt


def run_objective(request: RunRequest) -> RunReceipt:
    policy = evaluate_policy(request.objective)
    plan, planner = create_plan(request.objective, policy, request.use_ai)
    validations, artifact = execute_bounded(request.objective, policy, plan)

    if policy.risk_level == RiskLevel.PROTECTED:
        status = RunStatus.BLOCKED
        next_action = "Remove the protected operation or route it to an explicit human gate."
    elif all(item.passed for item in validations):
        status = RunStatus.VALIDATED
        next_action = "Review the evidence and export the bounded package to Codex."
    else:
        status = RunStatus.FAILED
        next_action = "Correct the failed validation before any further execution."

    receipt = RunReceipt(
        objective=request.objective,
        planner=planner,
        status=status,
        policy=policy,
        plan=plan,
        validations=validations,
        artifact_preview=artifact,
        next_action=next_action,
    )
    save_receipt(receipt)
    return receipt

from __future__ import annotations

from hashlib import sha256

from app.executor import execute_bounded
from app.models import EvidenceSummary, RiskLevel, RunReceipt, RunRequest, RunStatus
from app.planner import create_plan
from app.policy import evaluate_policy
from app.store import save_receipt


def run_objective(request: RunRequest) -> RunReceipt:
    policy = evaluate_policy(request.objective)
    plan, provenance = create_plan(request.objective, policy, request.use_ai)
    validations, artifact = execute_bounded(request.objective, policy, plan)
    artifact_sha256 = sha256(artifact.encode("utf-8")).hexdigest() if artifact else None

    if policy.risk_level == RiskLevel.PROTECTED:
        status = RunStatus.BLOCKED
        next_action = "Remove the protected operation or route it to an explicit human gate."
    elif all(item.passed for item in validations):
        status = RunStatus.VALIDATED
        next_action = "Review the evidence and export the bounded package to Codex."
    else:
        status = RunStatus.FAILED
        next_action = "Correct the failed validation before any further execution."

    passed = sum(item.passed for item in validations)
    if status == RunStatus.BLOCKED:
        evidence_text = (
            f"Protected run blocked safely; {passed}/{len(validations)} safety gates passed."
        )
    else:
        evidence_text = (
            f"{passed}/{len(validations)} validation gates passed; "
            f"artifact {'hashed' if artifact_sha256 else 'not produced'}."
        )

    receipt = RunReceipt(
        objective=request.objective,
        planner=provenance.model,
        planner_provenance=provenance,
        status=status,
        policy=policy,
        plan=plan,
        validations=validations,
        artifact_preview=artifact,
        artifact_sha256=artifact_sha256,
        evidence_summary=EvidenceSummary(
            passed=passed,
            total=len(validations),
            artifact_sha256=artifact_sha256,
            summary=evidence_text,
        ),
        next_action=next_action,
    )
    save_receipt(receipt)
    return receipt

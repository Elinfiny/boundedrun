from __future__ import annotations

import json
from hashlib import sha256

from app.models import ExecutionPlan, Handler, PolicyDecision, RiskLevel, ValidationResult

ALLOWED_HANDLERS = {
    Handler.DOCUMENTATION_UPDATE,
    Handler.CONFIGURATION_REVIEW,
    Handler.TEST_VALIDATION,
}


def _documentation_artifact(objective: str) -> str:
    return (
        "# Generated bounded work package\n\n"
        f"## Objective\n\n{objective.strip()}\n\n"
        "## Execution boundary\n\n"
        "- Operate only inside an isolated synthetic workspace.\n"
        "- Do not access secrets, production systems, money, PII, or external accounts.\n"
        "- Validate before accepting any result.\n\n"
        "## Required evidence\n\n"
        "- Policy decision\n- Validation results\n- Final receipt\n"
    )


def _configuration_artifact(objective: str) -> str:
    payload = {
        "objective": objective.strip(),
        "mode": "isolated-demo",
        "allowed_handlers": sorted(handler.value for handler in ALLOWED_HANDLERS),
        "network_access": False,
        "production_access": False,
        "requires_validation": True,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _test_artifact(objective: str) -> str:
    checks = {
        "objective_present": bool(objective.strip()),
        "minimum_length": len(objective.strip()) >= 8,
        "bounded_mode": True,
        "external_mutation": False,
    }
    return json.dumps(checks, indent=2, sort_keys=True)


def execute_bounded(
    objective: str, decision: PolicyDecision, plan: ExecutionPlan
) -> tuple[list[ValidationResult], str | None]:
    if decision.risk_level == RiskLevel.PROTECTED or plan.handler == Handler.NONE:
        return [
            ValidationResult(
                name="protected_boundary",
                passed=True,
                detail="Execution stopped before any protected operation.",
            )
        ], None

    if plan.handler not in ALLOWED_HANDLERS:
        return [
            ValidationResult(
                name="handler_allowlist",
                passed=False,
                detail=f"Handler {plan.handler.value} is not allow-listed.",
            )
        ], None

    if plan.handler == Handler.DOCUMENTATION_UPDATE:
        artifact = _documentation_artifact(objective)
        content_check = all(
            heading in artifact
            for heading in ("## Objective", "## Execution boundary", "## Required evidence")
        )
    elif plan.handler == Handler.CONFIGURATION_REVIEW:
        artifact = _configuration_artifact(objective)
        payload = json.loads(artifact)
        content_check = (
            payload["network_access"] is False
            and payload["production_access"] is False
            and payload["requires_validation"] is True
        )
    else:
        artifact = _test_artifact(objective)
        payload = json.loads(artifact)
        content_check = (
            payload["objective_present"] is True
            and payload["minimum_length"] is True
            and payload["bounded_mode"] is True
            and payload["external_mutation"] is False
        )

    digest = sha256(artifact.encode("utf-8")).hexdigest()
    validations = [
        ValidationResult(
            name="handler_allowlist",
            passed=True,
            detail=f"Approved handler: {plan.handler.value}",
        ),
        ValidationResult(
            name="artifact_contract",
            passed=content_check,
            detail="Generated artifact satisfies its deterministic contract.",
        ),
        ValidationResult(
            name="evidence_digest",
            passed=True,
            detail=f"SHA-256: {digest}",
        ),
        ValidationResult(
            name="protected_operations",
            passed=True,
            detail="No network, production, secret, financial, or destructive operation executed.",
        ),
    ]
    return validations, artifact

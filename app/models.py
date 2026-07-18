from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    SAFE = "safe"
    REVIEW = "review"
    PROTECTED = "protected"


class RunStatus(StrEnum):
    PLANNED = "planned"
    BLOCKED = "blocked"
    VALIDATED = "validated"
    FAILED = "failed"


class Handler(StrEnum):
    DOCUMENTATION_UPDATE = "documentation_update"
    CONFIGURATION_REVIEW = "configuration_review"
    TEST_VALIDATION = "test_validation"
    NONE = "none"


class RunRequest(BaseModel):
    objective: str = Field(min_length=8, max_length=1200)
    use_ai: bool = True


class PlanStep(BaseModel):
    order: int = Field(ge=1)
    action: str
    evidence: str


class ExecutionPlan(BaseModel):
    summary: str
    handler: Handler
    steps: list[PlanStep]
    validation_gates: list[str]
    protected_boundaries: list[str]


class PolicyDecision(BaseModel):
    risk_level: RiskLevel
    reasons: list[str]
    matched_terms: list[str] = Field(default_factory=list)
    allowed_actions: list[str]
    blocked_actions: list[str]


class ValidationResult(BaseModel):
    name: str
    passed: bool
    detail: str


class RunReceipt(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    objective: str
    planner: Literal["gpt-5.6", "deterministic"]
    status: RunStatus
    policy: PolicyDecision
    plan: ExecutionPlan
    validations: list[ValidationResult]
    artifact_preview: str | None = None
    next_action: str

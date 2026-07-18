from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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

    @field_validator("objective", mode="before")
    @classmethod
    def normalize_objective(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return " ".join(value.split())


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int = Field(ge=1)
    action: str = Field(min_length=3, max_length=240)
    evidence: str = Field(min_length=3, max_length=160)


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=8, max_length=600)
    handler: Handler
    steps: list[PlanStep] = Field(min_length=1, max_length=8)
    validation_gates: list[str] = Field(min_length=1, max_length=12)
    protected_boundaries: list[str] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def require_ordered_steps(self) -> ExecutionPlan:
        expected = list(range(1, len(self.steps) + 1))
        if [step.order for step in self.steps] != expected:
            raise ValueError("Plan steps must use contiguous order starting at 1")
        return self


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


class PlannerProvenance(BaseModel):
    source: Literal["openai_responses", "deterministic"]
    model: Literal["gpt-5.6", "deterministic"]
    ai_requested: bool
    ai_attempted: bool
    fallback_used: bool
    detail: str


class EvidenceSummary(BaseModel):
    passed: int = Field(ge=0)
    total: int = Field(ge=0)
    artifact_sha256: str | None = None
    summary: str


class RunReceipt(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    objective: str
    planner: Literal["gpt-5.6", "deterministic"]
    planner_provenance: PlannerProvenance | None = None
    status: RunStatus
    policy: PolicyDecision
    plan: ExecutionPlan
    validations: list[ValidationResult]
    artifact_preview: str | None = None
    artifact_sha256: str | None = None
    evidence_summary: EvidenceSummary | None = None
    next_action: str


class CodexWorkPackage(BaseModel):
    run_id: str
    normalized_objective: str
    policy_decision: PolicyDecision
    allowed_actions: list[str]
    blocked_actions: list[str]
    implementation_steps: list[PlanStep]
    validation_gates: list[str]
    protected_boundaries: list[str]
    evidence_requirements: list[str]
    repository_instructions: list[str]
    planner_provenance: PlannerProvenance
    artifact_sha256: str | None = None

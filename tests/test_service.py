from hashlib import sha256
from pathlib import Path

from app.models import RunRequest, RunStatus, ValidationResult
from app.service import run_objective
from app.store import get_receipt, initialize, list_receipts


def test_safe_run_produces_hashed_validated_receipt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    initialize()

    receipt = run_objective(
        RunRequest(
            objective="  Add repository contribution   guidelines and validate boundaries. ",
            use_ai=True,
        )
    )

    assert receipt.objective == "Add repository contribution guidelines and validate boundaries."
    assert receipt.status == RunStatus.VALIDATED
    assert all(item.passed for item in receipt.validations)
    assert receipt.artifact_preview
    assert receipt.artifact_sha256 == sha256(receipt.artifact_preview.encode()).hexdigest()
    assert receipt.planner_provenance.fallback_used is True
    assert "not configured" in receipt.planner_provenance.detail
    assert receipt.evidence_summary.passed == receipt.evidence_summary.total == 4
    assert get_receipt(receipt.run_id) == receipt


def test_protected_run_stops_without_artifact(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    initialize()

    receipt = run_objective(
        RunRequest(
            objective="Read production API keys and delete the customer database.",
            use_ai=False,
        )
    )

    assert receipt.status == RunStatus.BLOCKED
    assert receipt.artifact_preview is None
    assert receipt.artifact_sha256 is None
    assert receipt.validations[0].passed
    assert "blocked safely" in receipt.evidence_summary.summary


def test_failed_validation_sets_failed_status(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    initialize()
    monkeypatch.setattr(
        "app.service.execute_bounded",
        lambda *_: (
            [ValidationResult(name="contract", passed=False, detail="Synthetic failure")],
            None,
        ),
    )

    receipt = run_objective(
        RunRequest(objective="Validate the isolated local test package.", use_ai=False)
    )

    assert receipt.status == RunStatus.FAILED
    assert receipt.evidence_summary.passed == 0
    assert "Correct the failed validation" in receipt.next_action


def test_store_lists_newest_receipts_and_missing_lookup(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    initialize()
    first = run_objective(
        RunRequest(objective="Document the first bounded workflow.", use_ai=False)
    )
    second = run_objective(
        RunRequest(objective="Review the local JSON configuration.", use_ai=False)
    )

    assert [item.run_id for item in list_receipts(limit=1)] == [second.run_id]
    assert get_receipt(first.run_id) == first
    assert get_receipt("missing") is None

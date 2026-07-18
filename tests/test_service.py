from pathlib import Path

from app.models import RunRequest, RunStatus
from app.service import run_objective
from app.store import initialize


def test_safe_run_produces_validated_receipt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    initialize()
    receipt = run_objective(
        RunRequest(
            objective="Add repository contribution guidelines and validate governance boundaries.",
            use_ai=False,
        )
    )
    assert receipt.status == RunStatus.VALIDATED
    assert all(item.passed for item in receipt.validations)
    assert receipt.artifact_preview


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
    assert receipt.validations[0].passed

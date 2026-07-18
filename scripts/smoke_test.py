from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.main import app

SAFE_OBJECTIVE = "Add contribution guidelines and validate governance boundaries."
PROTECTED_OBJECTIVE = "Read the production API key and delete the customer database."


def run_smoke_test() -> dict[str, str]:
    original_directory = Path.cwd()
    with TemporaryDirectory(prefix="boundedrun-smoke-") as temporary_directory:
        os.chdir(temporary_directory)
        try:
            with TestClient(app) as client:
                health = client.get("/health")
                health.raise_for_status()

                safe = client.post(
                    "/api/runs",
                    json={"objective": SAFE_OBJECTIVE, "use_ai": False},
                )
                safe.raise_for_status()
                safe_receipt = safe.json()
                assert safe_receipt["status"] == "validated"
                assert all(item["passed"] for item in safe_receipt["validations"])

                protected = client.post(
                    "/api/runs",
                    json={"objective": PROTECTED_OBJECTIVE, "use_ai": False},
                )
                protected.raise_for_status()
                protected_receipt = protected.json()
                assert protected_receipt["status"] == "blocked"
                assert protected_receipt["artifact_preview"] is None

                run_id = safe_receipt["run_id"]
                exported = client.get(f"/api/runs/{run_id}/export?format=markdown")
                exported.raise_for_status()
                assert "BoundedRun Codex Work Package" in exported.text

                stored = client.get(f"/api/runs/{run_id}")
                stored.raise_for_status()
                assert stored.json() == safe_receipt
        finally:
            os.chdir(original_directory)

    return {
        "health": health.json()["status"],
        "safe_run": safe_receipt["status"],
        "protected_run": protected_receipt["status"],
        "export": "markdown downloaded",
        "stored_receipt": "reopened",
    }


if __name__ == "__main__":
    print(json.dumps(run_smoke_test(), indent=2))

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(app) as test_client:
        yield test_client


def create_safe_run(client: TestClient) -> dict:
    response = client.post(
        "/api/runs",
        json={
            "objective": "Validate the local configuration and produce an audit receipt.",
            "use_ai": False,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_dashboard_and_health_endpoints(client):
    dashboard = client.get("/")
    styles = client.get("/static/styles.css")
    health = client.get("/health")

    assert dashboard.status_code == 200
    assert "BoundedRun" in dashboard.text
    assert "Stored run history" in dashboard.text
    assert 'aria-live="polite"' in dashboard.text
    assert "Download Markdown" in dashboard.text
    assert "[hidden] { display: none !important; }" in styles.text
    assert health.json() == {"status": "ok", "service": "boundedrun"}


def test_create_list_and_reopen_stored_run(client):
    receipt = create_safe_run(client)

    recent = client.get("/api/runs?limit=1")
    reopened = client.get(f"/api/runs/{receipt['run_id']}")

    assert receipt["status"] == "validated"
    assert recent.status_code == 200
    assert recent.json()[0]["run_id"] == receipt["run_id"]
    assert reopened.json() == receipt


def test_markdown_and_json_exports_are_downloadable(client):
    receipt = create_safe_run(client)
    base = f"/api/runs/{receipt['run_id']}/export"

    markdown = client.get(base)
    json_export = client.get(f"{base}?format=json")
    package = json.loads(json_export.text)

    assert markdown.status_code == 200
    assert markdown.headers["content-type"].startswith("text/markdown")
    assert "attachment;" in markdown.headers["content-disposition"]
    assert "# BoundedRun Codex Work Package" in markdown.text
    assert "Repository-scoped Codex instructions" in markdown.text
    assert package["normalized_objective"] == receipt["objective"]
    assert package["artifact_sha256"] == receipt["artifact_sha256"]
    assert package["allowed_actions"]
    assert package["blocked_actions"]


@pytest.mark.parametrize(
    ("method", "path", "payload", "status"),
    [
        ("get", "/api/runs/missing", None, 404),
        ("get", "/api/runs/missing/export", None, 404),
        ("get", "/api/runs?limit=0", None, 422),
        ("get", "/api/runs/missing/export?format=xml", None, 422),
        ("post", "/api/runs", {"objective": "short"}, 422),
    ],
)
def test_api_errors_are_structured(client, method, path, payload, status):
    response = client.request(method, path, json=payload)

    assert response.status_code == status
    assert "detail" in response.json()

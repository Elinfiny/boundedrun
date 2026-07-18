from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_create_run_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={
                "objective": "Validate the local configuration and produce an audit receipt.",
                "use_ai": False,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "validated"

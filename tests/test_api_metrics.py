from fastapi.testclient import TestClient

from app.main import app


def test_initial_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "metrics.db"))
    with TestClient(app) as client:
        data = client.get("/metrics/summary").json()
        assert data["run_count"] == 0
        assert data["issue_count"] == 0
        assert data["median_resolution_minutes"] is None

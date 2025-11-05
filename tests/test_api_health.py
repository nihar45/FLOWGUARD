from fastapi.testclient import TestClient

from app.main import app


def test_health_response(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

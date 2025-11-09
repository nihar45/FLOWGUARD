from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_reject_prevents_retry(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "reject.db"))
    monkeypatch.setenv("FLOWGUARD_DATA_DIR", str(Path(__file__).resolve().parents[1] / "data"))
    with TestClient(app) as client:
        assert client.post("/runs").status_code == 200
        issue_id = client.get("/issues").json()[0]["id"]
        assert client.post(f"/issues/{issue_id}/reject", json={"actor": "reviewer"}).status_code == 200
        assert client.post(f"/issues/{issue_id}/retry", json={}).status_code == 409

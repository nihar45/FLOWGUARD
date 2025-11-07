from fastapi.testclient import TestClient

from app.main import app


def test_query_validation_and_empty_issue_list(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "queries.db"))
    with TestClient(app) as client:
        assert client.get("/issues").json() == []
        assert client.get("/runs?limit=0").status_code == 422
        assert client.get("/issues?limit=1001").status_code == 422
        assert client.get("/issues/999999").status_code == 404

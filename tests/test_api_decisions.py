from fastapi.testclient import TestClient

from app.main import app


def test_case_requires_approval_before_retry(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "cases.db"))
    monkeypatch.setenv("FLOWGUARD_DATA_DIR", str(__import__("pathlib").Path(__file__).resolve().parents[1] / "data"))
    with TestClient(app) as client:
        run = client.post("/runs")
        assert run.status_code == 200
        issues = client.get("/issues").json()
        assert issues
        issue_id = issues[0]["id"]
        assert client.post(f"/issues/{issue_id}/retry", json={"actor": "tester"}).status_code == 409
        assert client.post(f"/issues/{issue_id}/approve", json={"actor": "tester"}).status_code == 200
        assert client.post(f"/issues/{issue_id}/retry", json={"actor": "tester"}).status_code == 200
        details = client.get(f"/issues/{issue_id}").json()
        assert details["status"] == "recovered"
        assert [item["action"] for item in details["audit_history"]] == ["case_created", "approved", "retry"]

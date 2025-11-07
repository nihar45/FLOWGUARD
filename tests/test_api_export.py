from fastapi.testclient import TestClient

from app.main import app


def test_empty_export_has_csv_headers(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(tmp_path / "export.db"))
    with TestClient(app) as client:
        response = client.get("/exports/issues.csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

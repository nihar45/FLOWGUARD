from app.diagnosis import explain_issue


def test_fallback_diagnosis_when_unconfigured(monkeypatch):
    for key in ("FLOWGUARD_LLM_URL", "FLOWGUARD_LLM_API_KEY", "FLOWGUARD_LLM_MODEL"):
        monkeypatch.delenv(key, raising=False)
    result = explain_issue({"rule_id": "TEST_RULE", "dataset": "sales_orders", "record_ref": "42"})
    assert "TEST_RULE" in result
    assert "upstream" in result

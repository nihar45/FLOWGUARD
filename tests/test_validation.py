from pathlib import Path

from app.validation import load_sources, validate


def test_synthetic_fixture_detects_all_labeled_issues():
    root = Path(__file__).resolve().parents[1] / "data"
    sources = load_sources(root)
    detected = {finding.issue_key for finding in validate(sources)}
    expected = {
        "duplicate-order:SO-1002",
        "invalid-quantity:inventory:2",
        "orphan-install:INST-2004",
        "sku-mismatch:INST-2003",
        "install-over-order:SKU-A:INST-2005",
        "inventory-reconciliation:SKU-A",
    }
    assert expected <= detected


def test_schema_drift_stops_field_checks():
    from pandas import DataFrame

    sources = {
        "production": DataFrame({"wrong_column": [1]}),
        "inventory": DataFrame({"wrong_column": [1]}),
        "sales_orders": DataFrame({"wrong_column": [1]}),
        "installations": DataFrame({"wrong_column": [1]}),
    }
    findings = validate(sources)
    assert findings
    assert all(finding.rule_id == "SCHEMA_DRIFT" for finding in findings)

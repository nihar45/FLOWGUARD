from pathlib import Path

from app.validation import load_sources, validate


def test_source_csvs_load_with_expected_names():
    datasets = load_sources(Path(__file__).resolve().parents[1] / "data")
    assert set(datasets) == {"production", "inventory", "sales_orders", "installations"}
    assert all(len(frame) > 0 for frame in datasets.values())


def test_issue_keys_unique_for_synthetic_fixture():
    datasets = load_sources(Path(__file__).resolve().parents[1] / "data")
    keys = [finding.issue_key for finding in validate(datasets)]
    assert len(keys) == len(set(keys))

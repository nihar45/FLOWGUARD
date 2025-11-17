"""Print issues detected in the included synthetic fixture."""
from pathlib import Path
from app.validation import load_sources, validate

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "data"
    for issue in validate(load_sources(root)):
        print(f"{issue.severity:8} {issue.rule_id:36} {issue.issue_key}")

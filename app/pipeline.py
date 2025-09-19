from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from app import db
from app.diagnosis import explain_issue
from app.validation import load_sources, validate


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def data_dir() -> Path:
    return Path(os.getenv("FLOWGUARD_DATA_DIR", "./data"))


def run_validation() -> dict:
    started = utc_now()
    root = data_dir()
    sources = load_sources(root)
    findings = validate(sources)
    source_records = sum(len(frame) for frame in sources.values())
    expected_keys = set(json.loads((root / "known_issues.json").read_text()))
    expected_issue_count = len(expected_keys)
    completed = utc_now()
    notifications = []
    prepared_findings = []
    for finding in findings:
        item = finding.to_dict()
        item["diagnosis"] = explain_issue(item)
        prepared_findings.append(item)
    with db.connect() as conn:
        cursor = conn.execute(
            "INSERT INTO runs(started_at, completed_at, status, source_records, issue_count, expected_issue_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (started, completed, "completed", source_records, len(findings), expected_issue_count),
        )
        run_id = cursor.lastrowid
        for item in prepared_findings:
            cursor = conn.execute(
                """INSERT INTO issues(
                    run_id, issue_key, rule_id, dataset, record_ref, severity, impact_score,
                    title, details, diagnosis, suggested_action, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)""",
                (run_id, item["issue_key"], item["rule_id"], item["dataset"], item["record_ref"],
                 item["severity"], item["impact_score"], item["title"], item["details"],
                 item["diagnosis"], item["suggested_action"], completed),
            )
            issue_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO audit_events(issue_id, action, actor, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (issue_id, "case_created", "flowguard", "Validation rule opened this case.", completed),
            )
            notifications.append(item | {"id": issue_id, "run_id": run_id})
    for notification in notifications:
        _send_notification(notification)
    return {
        "id": run_id,
        "started_at": started,
        "completed_at": completed,
        "source_records": source_records,
        "issue_count": len(findings),
        "expected_issue_count": expected_issue_count,
    }


def _send_notification(issue: dict) -> None:
    url = os.getenv("FLOWGUARD_POWER_AUTOMATE_URL", "").strip()
    if not url:
        return
    try:
        requests.post(url, json=issue, timeout=5).raise_for_status()
    except requests.RequestException:
        # The local audit record is authoritative; notification failure does not erase the case.
        return

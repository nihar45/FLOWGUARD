from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from io import StringIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from app import db
from app.pipeline import run_validation, utc_now


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.initialize()
    yield


app = FastAPI(
    title="FlowGuard API",
    description="Synthetic solar operations data validation and human-reviewed workflow recovery.",
    version="0.1.0",
    lifespan=lifespan,
)


class Decision(BaseModel):
    actor: str = "reviewer"
    notes: str = ""


def _issue_payload(row: dict, events: list[dict] | None = None) -> dict:
    return row | ({"audit_history": events} if events is not None else {})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "flowguard-api"}


@app.post("/runs")
def create_run() -> dict:
    try:
        return run_validation()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=f"Source data file is missing: {exc.filename}") from exc
    except (ValueError, KeyError, pd.errors.ParserError) as exc:
        raise HTTPException(status_code=422, detail=f"Could not process source data: {exc}") from exc


@app.get("/runs")
def list_runs(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    with db.connect() as conn:
        rows = conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/issues")
def list_issues(
    status: str | None = None,
    run_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[dict]:
    clauses, params = [], []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if run_id is not None:
        clauses.append("run_id = ?")
        params.append(run_id)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with db.connect() as conn:
        rows = conn.execute(
            f"SELECT * FROM issues {where} ORDER BY impact_score DESC, id DESC LIMIT ?",
            (*params, limit),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/issues/{issue_id}")
def get_issue(issue_id: int) -> dict:
    with db.connect() as conn:
        issue = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")
        events = conn.execute(
            "SELECT * FROM audit_events WHERE issue_id = ? ORDER BY id", (issue_id,)
        ).fetchall()
    return _issue_payload(dict(issue), [dict(event) for event in events])


def _decide(issue_id: int, decision: Decision, action: str, new_status: str) -> dict:
    now = utc_now()
    with db.connect() as conn:
        issue = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")
        current = issue["status"]
        if action == "approved" and current != "open":
            raise HTTPException(status_code=409, detail="Only open cases can be approved")
        if action == "rejected" and current not in {"open", "approved"}:
            raise HTTPException(status_code=409, detail="This case can no longer be rejected")
        if action == "retry" and current != "approved":
            raise HTTPException(status_code=409, detail="Approve the recovery before retrying")
        resolved = now if new_status in {"recovered", "rejected"} else None
        conn.execute(
            "UPDATE issues SET status = ?, resolved_at = COALESCE(?, resolved_at) WHERE id = ?",
            (new_status, resolved, issue_id),
        )
        note = decision.notes.strip() or {
            "approved": "Reviewer approved the proposed simulated recovery.",
            "rejected": "Reviewer rejected the proposed recovery.",
            "retry": "Approved recovery was simulated; source data was not changed.",
        }[action]
        conn.execute(
            "INSERT INTO audit_events(issue_id, action, actor, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            (issue_id, action, decision.actor, note, now),
        )
    return get_issue(issue_id)


@app.post("/issues/{issue_id}/approve")
def approve_issue(issue_id: int, decision: Decision) -> dict:
    return _decide(issue_id, decision, "approved", "approved")


@app.post("/issues/{issue_id}/reject")
def reject_issue(issue_id: int, decision: Decision) -> dict:
    return _decide(issue_id, decision, "rejected", "rejected")


@app.post("/issues/{issue_id}/retry")
def retry_issue(issue_id: int, decision: Decision) -> dict:
    return _decide(issue_id, decision, "retry", "recovered")


@app.get("/metrics/summary")
def metrics_summary() -> dict:
    with db.connect() as conn:
        runs = conn.execute("SELECT COUNT(*) AS count FROM runs").fetchone()["count"]
        totals = conn.execute(
            "SELECT COUNT(*) AS total, SUM(status = 'open') AS open_count, "
            "SUM(status = 'recovered') AS recovered_count, SUM(status = 'rejected') AS rejected_count "
            "FROM issues"
        ).fetchone()
        latest_run = conn.execute("SELECT id, expected_issue_count FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        resolution = conn.execute(
            "SELECT (julianday(resolved_at) - julianday(created_at)) * 1440 AS minutes "
            "FROM issues WHERE resolved_at IS NOT NULL ORDER BY minutes"
        ).fetchall()
    durations = [max(0.0, row["minutes"]) for row in resolution if row["minutes"] is not None]
    median_resolution = float(pd.Series(durations).median()) if durations else None
    expected_keys_path = Path(os.getenv("FLOWGUARD_DATA_DIR", "./data")) / "known_issues.json"
    expected_keys = set(json.loads(expected_keys_path.read_text())) if expected_keys_path.exists() else set()
    if latest_run:
        with db.connect() as conn:
            latest_issues = conn.execute("SELECT issue_key FROM issues WHERE run_id = ?", (latest_run["id"],)).fetchall()
        latest_keys = {row["issue_key"] for row in latest_issues}
        detected = len(expected_keys & latest_keys)
        expected = latest_run["expected_issue_count"]
        latest_issue_count = len(latest_keys)
    else:
        detected = expected = latest_issue_count = 0
    return {
        "run_count": runs,
        "issue_count": totals["total"] or 0,
        "open_count": totals["open_count"] or 0,
        "recovered_count": totals["recovered_count"] or 0,
        "rejected_count": totals["rejected_count"] or 0,
        "expected_injected_issues": expected,
        "detected_injected_issues": detected,
        "injected_issue_detection_rate": round(detected / expected, 3) if expected else None,
        "latest_run_false_positives": max(0, latest_issue_count - detected),
        "median_resolution_minutes": round(median_resolution, 2) if median_resolution is not None else None,
    }


@app.get("/exports/issues.csv")
def export_issues() -> StreamingResponse:
    with db.connect() as conn:
        frame = pd.read_sql_query("SELECT * FROM issues ORDER BY run_id, id", conn)
    output = StringIO()
    frame.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flowguard-issues.csv"},
    )

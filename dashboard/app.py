from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


API_URL = os.getenv("FLOWGUARD_API_URL", "http://localhost:8000").rstrip("/")
st.set_page_config(page_title="FlowGuard Operations", page_icon="🛡️", layout="wide")
st.title("FlowGuard")
st.caption("Data quality and workflow recovery · simulated solar manufacturing operations")


def api_get(path: str):
    return requests.get(f"{API_URL}{path}", timeout=8)


def api_post(path: str, payload: dict | None = None):
    return requests.post(f"{API_URL}{path}", json=payload or {}, timeout=8)


try:
    api_get("/health").raise_for_status()
except requests.RequestException:
    st.error("FlowGuard API is not available. Start it with `uvicorn app.main:app --reload`.")
    st.stop()

if st.button("Run validation", type="primary"):
    try:
        response = api_post("/runs")
        response.raise_for_status()
        run = response.json()
        st.success(f"Run {run['id']} completed: {run['issue_count']} cases opened from {run['source_records']} records.")
    except requests.RequestException as exc:
        st.error(f"The validation run failed: {exc}")

try:
    summary = api_get("/metrics/summary").json()
    issues = api_get("/issues").json()
except requests.RequestException as exc:
    st.error(f"Could not load FlowGuard data: {exc}")
    st.stop()

metric_cols = st.columns(4)
metric_cols[0].metric("Open cases", summary["open_count"])
metric_cols[1].metric("Recovered", summary["recovered_count"])
detection = summary["injected_issue_detection_rate"]
metric_cols[2].metric("Seeded issue detection", f"{detection:.0%}" if detection is not None else "—")
resolution = summary["median_resolution_minutes"]
metric_cols[3].metric("Median resolution", f"{resolution:.1f} min" if resolution is not None else "—")

st.subheader("Investigation queue")
if not issues:
    st.info("No cases yet. Start a validation run to inspect the synthetic data.")
else:
    frame = pd.DataFrame(issues)
    visible = ["id", "title", "severity", "impact_score", "dataset", "status", "created_at"]
    st.dataframe(frame[visible], hide_index=True, use_container_width=True)
    labels = {f"#{row['id']} · {row['title']} · {row['status']}": row for row in issues}
    selected_label = st.selectbox("Review a case", list(labels))
    selected = labels[selected_label]
    details = api_get(f"/issues/{selected['id']}").json()
    st.markdown(f"**{details['details']}**")
    st.write("**Diagnosis**", details["diagnosis"])
    st.write("**Suggested next step**", details["suggested_action"])
    st.caption(f"Rule: {details['rule_id']} · Impact score: {details['impact_score']}/5 · Source: {details['dataset']}")

    actor = st.text_input("Reviewer", value="operations-reviewer", key=f"actor-{selected['id']}")
    notes = st.text_input("Review note", key=f"notes-{selected['id']}")
    actions = st.columns(3)
    if selected["status"] == "open":
        if actions[0].button("Approve recovery", key=f"approve-{selected['id']}"):
            response = api_post(f"/issues/{selected['id']}/approve", {"actor": actor, "notes": notes})
            if response.ok:
                st.success("Approved and added to the audit history.")
                st.rerun()
            st.error(response.text)
        if actions[1].button("Reject", key=f"reject-{selected['id']}"):
            response = api_post(f"/issues/{selected['id']}/reject", {"actor": actor, "notes": notes})
            if response.ok:
                st.success("Rejection recorded.")
                st.rerun()
            st.error(response.text)
    elif selected["status"] == "approved":
        if actions[0].button("Simulate retry", key=f"retry-{selected['id']}"):
            response = api_post(f"/issues/{selected['id']}/retry", {"actor": actor, "notes": notes})
            if response.ok:
                st.success("Retry simulated. Source files were not changed.")
                st.rerun()
            st.error(response.text)
    with st.expander("Audit history"):
        st.dataframe(pd.DataFrame(details["audit_history"]), hide_index=True, use_container_width=True)

st.divider()
st.caption("Source records remain unchanged. AI explanations are advisory; reviewer approval is required before a simulated retry.")

from __future__ import annotations

import os

import requests


def explain_issue(issue: dict) -> str:
    """Use an optional compatible LLM endpoint, with a safe deterministic fallback."""
    fallback = (
        f"{issue['rule_id']} detected in {issue['dataset']} at {issue['record_ref']}. "
        "Compare the source records named in the case, confirm the intended business value, "
        "and correct the upstream source before rerunning the simulated workflow."
    )
    endpoint = os.getenv("FLOWGUARD_LLM_URL", "").strip()
    api_key = os.getenv("FLOWGUARD_LLM_API_KEY", "").strip()
    model = os.getenv("FLOWGUARD_LLM_MODEL", "").strip()
    if not endpoint or not api_key or not model:
        return fallback

    prompt = (
        "Explain this synthetic solar-operations data issue in plain language. "
        "Suggest a safe next step for a human reviewer. Do not claim to change data, "
        "do not invent facts, and do not approve or execute a fix.\n\n"
        f"Case: {issue['title']}\nRule: {issue['rule_id']}\n"
        f"Details: {issue['details']}\nProposed action: {issue['suggested_action']}"
    )
    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You provide cautious data-quality triage."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            },
            timeout=12,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if isinstance(content, str) and content.strip():
            return content.strip()[:2000]
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        pass
    return fallback

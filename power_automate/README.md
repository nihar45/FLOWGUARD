# Power Automate notification flow

This proof of concept can notify a Power Automate flow when validation opens a case.

1. Create an **Automated cloud flow** with the **When an HTTP request is received** trigger.
2. Define a JSON schema from a sample FlowGuard case payload. Useful fields include `id`, `run_id`, `rule_id`, `severity`, `impact_score`, `title`, `details`, `diagnosis`, and `suggested_action`.
3. Add a Teams or Outlook notification action for the operations review group. Include the case ID and a link to the FlowGuard dashboard.
4. Optionally add an approval card. The approval should direct reviewers to FlowGuard; record their decision through `POST /issues/{id}/approve` or `/reject` so the platform keeps one audit trail.
5. Store the trigger URL in `FLOWGUARD_POWER_AUTOMATE_URL` in a local `.env` file. Do not commit the URL or share it publicly.

The notification is best-effort: a Power Automate outage does not remove or hide the investigation case in FlowGuard.

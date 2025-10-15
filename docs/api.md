# API reference

OpenAPI is available at `/docs` when the FastAPI server is running.

- `GET /health` returns service health.
- `POST /runs` validates the configured inputs and opens issues.
- `GET /runs` lists run summaries.
- `GET /issues` filters by status and run ID.
- `GET /issues/{issue_id}` returns a case with its audit history.
- `POST /issues/{issue_id}/approve` transitions open to approved.
- `POST /issues/{issue_id}/reject` transitions open/approved to rejected.
- `POST /issues/{issue_id}/retry` transitions approved to recovered; it simulates recovery without source edits.
- `GET /metrics/summary` returns KPIs.
- `GET /exports/issues.csv` exports a case table.

Approval is a human decision; external model output never performs state transitions.

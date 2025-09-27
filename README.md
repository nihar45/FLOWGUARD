# FlowGuard

**AI-assisted data quality and workflow recovery for solar operations.**

FlowGuard is a portfolio proof of concept for a simulated solar manufacturer. It ingests production, inventory, sales, and installation data; detects data quality and cross-system issues; opens investigation cases; suggests safe next steps; and records human decisions before simulating a retry. Source files are never modified by recovery actions.

All included data is synthetic. The project is inspired by operational reporting work in solar manufacturing, but is an independent demo.

## MVP workflow

1. Start a validation run against the four CSV files in `data/`.
2. Check schemas, duplicates, invalid quantities, missing references, and cross-system reconciliation.
3. Rank cases using severity and estimated business impact.
4. Generate a rule-based diagnosis, with optional LLM assistance when configured.
5. Review, approve, reject, or retry a case. Every action is written to an audit log.
6. View operational metrics in the Streamlit dashboard or export the data for Power BI.

## Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```bash
streamlit run dashboard/app.py
```

Open the API docs at `http://localhost:8000/docs` and the dashboard at `http://localhost:8501`. The dashboard starts with a **Run validation** button. `POST /runs` starts the same workflow through the API.

## Docker

```bash
docker compose up --build
```

The API is on port 8000 and the dashboard on port 8501. SQLite data is persisted in the `flowguard_data` Docker volume.

## Useful API routes

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/runs` | Validate all source datasets and open cases |
| `GET` | `/runs` | List validation runs |
| `GET` | `/issues` | Filter cases by run or status |
| `GET` | `/issues/{id}` | View a case and its audit history |
| `POST` | `/issues/{id}/approve` | Approve the proposed simulated recovery |
| `POST` | `/issues/{id}/reject` | Reject a proposed recovery |
| `POST` | `/issues/{id}/retry` | Simulate retry after approval |
| `GET` | `/metrics/summary` | Dashboard KPIs |
| `GET` | `/exports/issues.csv` | Power BI friendly issue export |

## Optional integrations

Copy `.env.example` to `.env` and configure only the integrations you want:

- `FLOWGUARD_POWER_AUTOMATE_URL`: an HTTP-triggered Power Automate flow URL. FlowGuard posts a new-case notification payload when a run finds issues. Keep this URL private.
- `FLOWGUARD_LLM_URL`, `FLOWGUARD_LLM_API_KEY`, and `FLOWGUARD_LLM_MODEL`: an OpenAI-compatible chat-completions endpoint for diagnosis assistance. With no key, FlowGuard uses deterministic rule-based explanations. The model can suggest a fix, but cannot approve or apply it.

## Power Automate setup

See [`power_automate/README.md`](power_automate/README.md) for the notification and human approval flow outline. The proof of concept sends case notifications; approval decisions are recorded through FlowGuard's API so the audit history remains in one place.

## Power BI

Use **Get Data → Web** with `http://localhost:8000/metrics/summary` for KPI values and `http://localhost:8000/exports/issues.csv` for case-level analysis. For a deployed instance, replace `localhost` with the API host. Suggested visuals: cases by rule and severity, cases by status, detection rate by run, and resolution time. The included Streamlit page is the runnable demo dashboard; a `.pbix` file is not included.

## Metrics

The demo reports detection rate against known injected issues, false-positive rate against the labeled synthetic dataset, open/recovered case counts, and median time to resolution. The seeded data has known expected cases so those values can be evaluated rather than guessed. Time-based metrics use recorded case/action timestamps and will be sparse until cases are worked through the UI.

## Safety and scope

- Recovery is simulated; FlowGuard does not write to source systems.
- Approval is required before a retry can be recorded.
- AI output is advisory and treated as untrusted text.
- This is a proof of concept, not a production incident-management or data-governance system.

## Project layout

```text
app/                 FastAPI service, validation, persistence, recovery
dashboard/           Streamlit operations and review dashboard
data/                Synthetic, intentionally imperfect source files
power_automate/      Optional integration setup notes
tests/               Focused tests for validation and recovery rules
```

## Build history

Commits document the work as it is actually completed. They should not be backdated to suggest an earlier development period.

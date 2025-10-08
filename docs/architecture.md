# Architecture

The FastAPI service is the system of record for validation runs, issues, and reviewer actions. `app/validation.py` detects problems in CSV sources. `app/pipeline.py` persists cases and writes an audit event before optionally notifying Power Automate. `app/diagnosis.py` generates a deterministic diagnosis and optionally asks an external model for advisory text. The Streamlit dashboard calls the API instead of accessing SQLite directly.

## Trust boundaries

CSV inputs are untrusted; missing columns generate schema-drift cases. Model output is advisory only. The SQLite audit log records state changes. Recovery is simulated, and source CSVs are never rewritten.

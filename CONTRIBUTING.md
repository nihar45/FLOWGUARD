# Contributing

Keep validation functions deterministic and test them with small fixtures. Do not commit actual customer data, `.env`, credentials, or local SQLite files. Run `python -m pytest -q` before submitting changes. Add an API contract update whenever an endpoint or state transition changes. Never claim simulated recovery modified the source files.

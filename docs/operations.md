# Operations runbook

**API unavailable:** confirm `uvicorn app.main:app` is running and the chosen port is free. **Missing CSV:** verify `FLOWGUARD_DATA_DIR` contains all four expected files. **SQLite locked:** stop duplicate writers and check the configured database path. **No LLM response:** rule-based diagnosis is used automatically. **Webhook failure:** local cases persist, but the demo does not provide a delivery retry queue.

Back up SQLite before replacing the database. The app has no migration framework, so schema changes need separate migration planning.

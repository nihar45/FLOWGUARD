# ADR-0001: SQLite for the prototype

**Decision:** Persist runs, cases, and audit events in SQLite. This keeps local evaluation reproducible with no external database service. **Trade-off:** SQLite is not a substitute for a multi-user operational datastore; concurrency, migrations, replication, and access governance remain out of scope.

# ADR-0003: Best-effort case notifications

**Decision:** Commit cases to SQLite before attempting a Power Automate notification. Notification failure does not delete or invalidate local state. **Trade-off:** failed notifications are not automatically retried; production systems should use a durable outbox and delivery acknowledgements.

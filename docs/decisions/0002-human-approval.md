# ADR-0002: Human-controlled recovery

**Decision:** The system requires an explicit reviewer approval before recording a simulated retry. Model-supplied explanations are advisory. This keeps generated prose outside the execution path and provides an auditable decision trail. **Trade-off:** reviewer labels are not authenticated in this demo.

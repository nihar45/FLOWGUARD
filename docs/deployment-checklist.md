# Deployment readiness

- [ ] Implement authentication and authorization for all case-mutating routes.
- [ ] Replace free-text actor identifiers with server-derived user IDs.
- [ ] Require TLS and use managed credential storage.
- [ ] Add input bounds, rate limits, and operational monitoring.
- [ ] Add a database migration mechanism and backup/restore drills.
- [ ] Introduce durable notification retries and outbound endpoint allowlisting.
- [ ] Remove or separately protect synthetic label files.
- [ ] Pin dependencies and add dependency scanning.

Until these conditions are met, use only in a trusted demonstration environment.

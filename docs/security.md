# Security scope

This is a local proof of concept, not a production incident-management service.

## Current constraints

- API endpoints do **not** authenticate callers, including approval and retry actions.
- Dashboard reviewer names are supplied as text and are not verified identities.
- Optional LLM credentials are read from environment variables and sent as Bearer tokens only to the configured LLM URL.
- Power Automate webhook URLs may embed a secret and must remain private.
- Database and CSV files are local; no production authorization boundary is provided.

## Production prerequisites

Implement user authentication and role-based authorization, server-side actor identity, audit integrity controls, rate limiting, input size limits, TLS, managed secrets, and webhook signing/verification before exposing beyond a trusted test environment.

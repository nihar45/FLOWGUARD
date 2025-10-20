# Configuration

| Variable | Description |
| --- | --- |
| `FLOWGUARD_DB_PATH` | SQLite location; default `./flowguard.db` |
| `FLOWGUARD_DATA_DIR` | Input CSV directory; default `./data` |
| `FLOWGUARD_API_URL` | Dashboard API base URL |
| `FLOWGUARD_POWER_AUTOMATE_URL` | Optional notification webhook; treat as a secret |
| `FLOWGUARD_LLM_URL` | Optional LLM-compatible endpoint |
| `FLOWGUARD_LLM_API_KEY` | Optional outbound LLM credential; never log or commit |
| `FLOWGUARD_LLM_MODEL` | Model identifier for advisory explanations |

The demo does not provide user accounts or enforce authentication. Deploy only in a trusted local/test environment, or place it behind an authenticated gateway. The LLM key does not authenticate callers to FlowGuard.

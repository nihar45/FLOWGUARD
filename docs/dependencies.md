# Dependency management

FLOWGUARD uses Python 3.11+ and declares application dependencies in
`pyproject.toml`. The layered requirements files give convenient installations
for the API, dashboard, and development environment.

| Package | Constraint | Role | Install group |
| --- | --- | --- | --- |
| `fastapi` | `>=0.115,<1` | HTTP API and routing | API |
| `uvicorn[standard]` | `>=0.30,<1` | ASGI serving and performance-related extras | API |
| `pandas` | `>=2.2,<3` | Tabular data ingestion and validation | API |
| `requests` | `>=2.32,<3` | Outbound HTTP integration | API |
| `python-dotenv` | `>=1.0,<2` | Loading environment configuration | API |
| `streamlit` | `>=1.40,<2` | Optional interactive dashboard | Dashboard |
| `pytest` | `>=8,<9` | Automated testing | Development |
| `httpx` | `>=0.27,<1` | TestClient HTTP integration | Development |
| `setuptools` | `>=68` | Python package build backend | Build only |

The standard-library modules (`sqlite3`, `json`, `pathlib`, etc.) ship with
Python and do not require pip installation. Transitive dependencies are
resolved by pip and are **not** listed individually as direct requirements.

## Install

```bash
# API only
python -m pip install -r requirements-api.txt

# API plus dashboard
python -m pip install -r requirements-dashboard.txt

# All demo and testing tools (also used by the Dockerfile and CI)
python -m pip install -r requirements.txt
python -m pytest -q
```

`requirements.txt` includes `requirements-dev.txt`, which includes
`requirements-dashboard.txt`, which includes `requirements-api.txt`. The Docker
image currently includes development tools to preserve its existing behavior;
a production image should install only its required group.

These files express compatibility ranges, **not a pinned lockfile**; actual
transitive versions depend on the install date and Python version. For a
production deployment, generate and review a pinned lockfile, scan dependencies
for vulnerabilities, and test upgrades in CI. Do not commit `site-packages/`,
virtual environments, cached installers, or third-party package source trees.

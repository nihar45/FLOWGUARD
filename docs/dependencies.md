# Dependency management

Use `requirements.txt` for the demo environment and `pyproject.toml` for package metadata. Dependencies use compatibility ranges, not a reproducible lockfile. A deployed application should pin and review a lockfile and run vulnerability checks. CI validates functional tests but does not provide a security audit.

# Contributing

Thanks for considering a contribution. This project is intentionally small
in scope - see README.md's "What this is not" section before proposing a
new feature; capabilities outside that scope (polygon operations, CRS
transforms, routing, geocoding) are likely out of scope for this
repository.

## Development setup

```bash
git clone <repository-url>
cd aei-geo-features
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Before opening a pull request

- Add or update tests for any behavior change.
- Keep the public API narrow - prefer fixing/clarifying an existing
  function over adding a new one, unless it's a clear gap in the stated
  scope (distance, jitter, normalization, validation).
- Do not add a new hard runtime dependency without discussion first -
  open an issue describing the use case.
- Run `pytest` locally; CI will also run it against all supported Python
  versions.

## Reporting bugs vs. reporting vulnerabilities

Functional bugs: open a GitHub issue.
Security vulnerabilities: see `SECURITY.md` - do not open a public issue.

## Code of conduct

Be respectful and constructive. Maintainers may close issues or PRs that
are off-topic, abusive, or outside this project's stated scope.

# Publishing preparation (not active)

**There is no publishing workflow in this repository.** This document only
records what a future, explicitly-approved publish workflow would look
like, using PyPI's Trusted Publishing (OIDC) mechanism, so that no PyPI
API token ever needs to be created, stored, or embedded in this project's
CI configuration.

Nothing in this document should be turned into an active workflow file
without a separate, explicit approval step - this file is documentation
only.

## Why Trusted Publishing instead of a token

PyPI Trusted Publishing lets a specific GitHub Actions workflow
(identified by repo, workflow filename, and environment) request a
short-lived upload credential directly from PyPI via OpenID Connect (OIDC)
at publish time. There is no long-lived `PYPI_API_TOKEN` secret to create,
rotate, store in GitHub Secrets, or accidentally leak in a log.

## Prerequisites before this could ever be turned on

1. The public GitHub repository must actually exist (it does not yet).
2. A PyPI project named `aei-geo-features` must exist or be claimable, and
   an owner/maintainer account must register it as a Trusted Publisher for
   the exact GitHub repo + workflow filename + (optionally) environment
   that will run the publish step. This is done on pypi.org, not in this
   repository.
3. Explicit, separate approval to actually publish - this is a distinct
   decision from approving this release candidate's code.

## What the (currently absent) publish workflow would contain

A separate file, e.g. `.github/workflows/publish.yml`, triggered only on
a GitHub Release being published (not on every push to `main`):

```yaml
# NOT AN ACTIVE FILE - illustrative only. Do not add this file to
# .github/workflows/ without explicit, separate approval.
name: Publish to PyPI
on:
  release:
    types: [published]
permissions:
  id-token: write   # required for OIDC trusted publishing
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # No `password`/`api-token` input - trusted publishing handles auth.
```

Key properties of that (still hypothetical) workflow:
- Triggered only by a maintainer publishing a GitHub Release - never on
  every commit to `main`.
- No secret of any kind stored in this repository or its Actions
  configuration.
- Uses a GitHub Actions "environment" (e.g. `pypi`) so the publish step
  can additionally be gated with required reviewers if desired.

## Current state

- No PyPI project has been registered.
- No Trusted Publisher relationship has been configured on PyPI.
- No publish workflow file exists in `.github/workflows/`.
- `ci.yml` builds and validates the wheel/sdist on every PR and push to
  `main` but uploads nothing anywhere.

# Publishing process

**This repository publishes to PyPI using `.github/workflows/publish.yml`.**
It uses PyPI's Trusted Publishing (OIDC) mechanism exclusively - no PyPI
API token is created, stored, or embedded anywhere in this project's CI
configuration.

## How a release is published

- **Normal path**: a maintainer publishes a GitHub Release. This fires
  the workflow's `release: published` trigger, which builds the wheel/
  sdist and publishes them to production PyPI (`environment: pypi`).
- **Manual path**: the workflow can also be run manually via
  `workflow_dispatch` with a `target` input of `testpypi` (default) or
  `pypi`. This exists because GitHub does not reliably re-fire the
  `release: published` trigger when a release is republished against an
  already-existing tag - see
  https://github.com/orgs/community/discussions/54574. A manual run
  always requires `target` to be chosen explicitly; `pypi` is never the
  default.

Both paths run through the same `build` job first, and both publish
jobs are mutually exclusive - only one of `publish-testpypi` /
`publish-pypi` ever runs for a given trigger.

## Why Trusted Publishing instead of a token

PyPI Trusted Publishing lets a specific GitHub Actions workflow
(identified by repo, workflow filename, and environment) request a
short-lived upload credential directly from PyPI via OpenID Connect (OIDC)
at publish time. There is no long-lived `PYPI_API_TOKEN` secret to create,
rotate, store in GitHub Secrets, or accidentally leak in a log.

## Trusted Publisher registration

`aei-geo-features` is registered as a Trusted Publisher on both pypi.org
and test.pypi.org, tied to this exact GitHub repository, the
`publish.yml` workflow filename, and the `pypi`/`testpypi` environments
respectively. That registration is done on PyPI's own site (Account
Settings -> Publishing), not in this repository - there is nothing to
configure here beyond the workflow file itself.

## What `.github/workflows/publish.yml` actually contains

See the file directly for the exact, current definition. In summary: a
`build` job (checkout, build wheel/sdist, `twine check`, upload as an
artifact) followed by two mutually-exclusive publish jobs
(`publish-testpypi`, `publish-pypi`), each using
`pypa/gh-action-pypi-publish` pinned to an immutable commit SHA and each
scoped to its own GitHub Actions environment with `id-token: write`. No
`push` or `pull_request` trigger exists anywhere in the workflow, so an
ordinary commit can never publish anything.

## Current state

- The PyPI project exists: https://pypi.org/project/aei-geo-features/
- Trusted Publisher relationships are configured on both pypi.org and
  test.pypi.org.
- `.github/workflows/publish.yml` is active and has been used for real
  releases.
- `ci.yml` separately builds and validates the wheel/sdist on every PR and
  push to `main`, but never uploads anywhere - it is unrelated to
  publishing.

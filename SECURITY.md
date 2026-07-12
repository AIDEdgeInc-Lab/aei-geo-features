# Security Policy

## Supported versions

This project is published on PyPI (https://pypi.org/project/aei-geo-features/).
Only the latest published version and the latest commit on `main` are
supported.

| Version | Supported |
|---|---|
| 0.1.x | Yes, best-effort |
| < 0.1.0 | No |

## Reporting a vulnerability

**Please do not open a public GitHub issue for a suspected security
vulnerability.**

Report vulnerabilities privately using GitHub's private vulnerability
reporting (Security tab -> "Report a vulnerability") on the repository,
which opens a private advisory visible only to maintainers. If that
channel is unavailable, contact the maintainers through a private channel
and avoid including exploit details in any public forum.

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce, or a minimal proof of concept
- The affected version(s)

## What to expect

- We will acknowledge receipt as soon as reasonably possible.
- We do not commit to a specific response-time or fix-time service level
  agreement (SLA). This is a small, community-maintained-scale project,
  not a commercially supported product.
- We will credit reporters who wish to be credited, once a fix is
  released.

## Scope

This library performs coordinate math and pandas DataFrame transformations
only. It does not make network calls, does not read environment variables,
and does not execute arbitrary code from its inputs. The most relevant
security-adjacent property to verify in any report is that these
guarantees still hold.

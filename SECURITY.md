# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email security concerns to: security@example.com

We will respond within 72 hours and issue a patch release as needed.

## Scope

agent-policy is a pure-Python library with zero runtime dependencies.
Security concerns typically relate to:
- Policy bypass (allow rules incorrectly overriding deny rules).
- Wildcard expansion edge cases.
- Conditions comparison logic.

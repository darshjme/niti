# Changelog

All notable changes to **agent-policy** are documented here.

## [1.0.0] — 2026-03-25

### Added
- `Permission` with wildcard matching and conditional guards.
- `Policy` with fluent `add_permission` / `add_deny` API.
- `PolicyEngine` supporting multiple policies per agent.
- `PolicyResult` dataclass with `to_dict()` and `__bool__`.
- `@require_permission` decorator raising `PermissionDeniedError`.
- 22 pytest unit tests — 100% passing.
- Zero runtime dependencies; Python 3.10+.

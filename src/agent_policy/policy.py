"""Policy: a named set of allow/deny permissions."""

from __future__ import annotations
from typing import Optional

from .permission import Permission


class Policy:
    """A named collection of allow and deny permissions.

    Deny rules take precedence over allow rules (explicit deny overrides allow).

    Args:
        name:        Unique policy name.
        permissions: Initial allow-list.
        deny:        Initial deny-list.
    """

    def __init__(
        self,
        name: str,
        permissions: Optional[list[Permission]] = None,
        deny: Optional[list[Permission]] = None,
    ) -> None:
        if not name:
            raise ValueError("Policy name must be a non-empty string")
        self.name = name
        self._allow: list[Permission] = list(permissions or [])
        self._deny: list[Permission] = list(deny or [])

    # ------------------------------------------------------------------
    def add_permission(self, perm: Permission) -> "Policy":
        """Append an allow permission. Returns *self* for fluent chaining."""
        if not isinstance(perm, Permission):
            raise TypeError("perm must be a Permission instance")
        self._allow.append(perm)
        return self

    def add_deny(self, perm: Permission) -> "Policy":
        """Append a deny permission. Returns *self* for fluent chaining."""
        if not isinstance(perm, Permission):
            raise TypeError("perm must be a Permission instance")
        self._deny.append(perm)
        return self

    # ------------------------------------------------------------------
    def allows(
        self,
        resource: str,
        action: str,
        context: Optional[dict] = None,
    ) -> bool:
        """Return True only if an allow rule matches AND no deny rule matches."""
        # Explicit deny always wins
        for perm in self._deny:
            if perm.matches(resource, action, context):
                return False
        # Must have at least one matching allow rule
        for perm in self._allow:
            if perm.matches(resource, action, context):
                return True
        return False

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "allow": [p.to_dict() for p in self._allow],
            "deny": [p.to_dict() for p in self._deny],
        }

    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Policy(name={self.name!r}, allow={len(self._allow)}, "
            f"deny={len(self._deny)})"
        )

"""Permission: a single allowed action on a resource."""

from __future__ import annotations
import fnmatch
from typing import Optional


class Permission:
    """Represents a single permission granting or matching an action on a resource.

    Supports wildcard matching via ``fnmatch`` patterns, e.g. ``resource="db:*"``.

    Args:
        resource: The resource identifier (may contain ``*`` wildcards).
        action:   The action identifier (may contain ``*`` wildcards).
        conditions: Optional dict of extra conditions that must match the
                    evaluation ``context`` for this permission to apply.
    """

    def __init__(
        self,
        resource: str,
        action: str,
        conditions: Optional[dict] = None,
    ) -> None:
        if not resource:
            raise ValueError("resource must be a non-empty string")
        if not action:
            raise ValueError("action must be a non-empty string")
        self.resource = resource
        self.action = action
        self.conditions: dict = conditions or {}

    # ------------------------------------------------------------------
    def matches(
        self,
        resource: str,
        action: str,
        context: Optional[dict] = None,
    ) -> bool:
        """Return True if this permission covers the given resource/action/context.

        Wildcard matching (``fnmatch``) is applied to both resource and action.
        All declared conditions must appear in *context* with equal values.
        """
        if not fnmatch.fnmatchcase(resource, self.resource):
            return False
        if not fnmatch.fnmatchcase(action, self.action):
            return False
        if self.conditions:
            ctx = context or {}
            for key, expected in self.conditions.items():
                if ctx.get(key) != expected:
                    return False
        return True

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        d: dict = {"resource": self.resource, "action": self.action}
        if self.conditions:
            d["conditions"] = dict(self.conditions)
        return d

    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Permission(resource={self.resource!r}, action={self.action!r}, "
            f"conditions={self.conditions!r})"
        )

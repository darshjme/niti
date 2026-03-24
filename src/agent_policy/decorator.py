"""@require_permission decorator."""

from __future__ import annotations
import functools
from typing import TYPE_CHECKING

from .exceptions import PermissionDeniedError

if TYPE_CHECKING:
    from .engine import PolicyEngine


def require_permission(
    engine: "PolicyEngine",
    agent_id: str,
    resource: str,
    action: str,
    context: dict | None = None,
):
    """Decorator that guards a function with a policy check.

    Raises :class:`PermissionDeniedError` if the engine denies the action.

    Usage::

        engine = PolicyEngine()
        # ... attach policies ...

        @require_permission(engine, agent_id="agent-A", resource="db", action="read")
        def fetch_records():
            return db.query(...)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = engine.check(agent_id, resource, action, context)
            if not result.allowed:
                raise PermissionDeniedError(
                    agent_id=agent_id,
                    resource=resource,
                    action=action,
                    reason=result.reason,
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator

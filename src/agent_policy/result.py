"""PolicyResult: the outcome of a policy check."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PolicyResult:
    """Immutable access-decision record returned by :class:`PolicyEngine.check`.

    Attributes:
        allowed:   Whether the action is permitted.
        reason:    Human-readable explanation.
        agent_id:  The agent that was evaluated.
        resource:  The resource that was checked.
        action:    The action that was checked.
    """

    allowed: bool
    reason: str
    agent_id: str
    resource: str
    action: str

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "agent_id": self.agent_id,
            "resource": self.resource,
            "action": self.action,
        }

    # ------------------------------------------------------------------
    def __bool__(self) -> bool:  # convenience: ``if result:``
        return self.allowed

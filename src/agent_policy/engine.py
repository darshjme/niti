"""PolicyEngine: evaluates multiple policies for agents."""

from __future__ import annotations
from collections import defaultdict
from typing import Optional

from .policy import Policy
from .result import PolicyResult


class PolicyEngine:
    """Central engine that attaches policies to agents and evaluates access.

    Multiple policies can be attached to a single agent; the engine applies
    an *any-allow / any-deny* strategy:

    * If **any** attached policy explicitly denies → denied.
    * If **any** attached policy allows (and none deny) → allowed.
    * If **no** policy allows → denied.
    """

    def __init__(self) -> None:
        # agent_id → list[Policy]
        self._registry: dict[str, list[Policy]] = defaultdict(list)

    # ------------------------------------------------------------------
    def attach(self, agent_id: str, policy: Policy) -> None:
        """Attach *policy* to *agent_id*.  Duplicate names are replaced."""
        if not isinstance(policy, Policy):
            raise TypeError("policy must be a Policy instance")
        # Remove existing policy with same name to avoid duplicates
        self._registry[agent_id] = [
            p for p in self._registry[agent_id] if p.name != policy.name
        ]
        self._registry[agent_id].append(policy)

    def detach(self, agent_id: str, policy_name: str) -> None:
        """Detach the policy named *policy_name* from *agent_id*."""
        self._registry[agent_id] = [
            p for p in self._registry[agent_id] if p.name != policy_name
        ]

    # ------------------------------------------------------------------
    def policies_for(self, agent_id: str) -> list[Policy]:
        """Return all policies attached to *agent_id*."""
        return list(self._registry.get(agent_id, []))

    # ------------------------------------------------------------------
    def check(
        self,
        agent_id: str,
        resource: str,
        action: str,
        context: Optional[dict] = None,
    ) -> PolicyResult:
        """Evaluate whether *agent_id* may perform *action* on *resource*.

        Returns a :class:`PolicyResult` with the decision and reason.
        """
        policies = self._registry.get(agent_id, [])
        if not policies:
            return PolicyResult(
                allowed=False,
                reason=f"No policies attached to agent '{agent_id}'",
                agent_id=agent_id,
                resource=resource,
                action=action,
            )

        # Pass 1: check for any explicit deny across all policies
        for policy in policies:
            for perm in policy._deny:
                if perm.matches(resource, action, context):
                    return PolicyResult(
                        allowed=False,
                        reason=(
                            f"Explicitly denied by policy '{policy.name}' "
                            f"(resource={resource!r}, action={action!r})"
                        ),
                        agent_id=agent_id,
                        resource=resource,
                        action=action,
                    )

        # Pass 2: check for any allow
        for policy in policies:
            for perm in policy._allow:
                if perm.matches(resource, action, context):
                    return PolicyResult(
                        allowed=True,
                        reason=(
                            f"Allowed by policy '{policy.name}' "
                            f"(resource={resource!r}, action={action!r})"
                        ),
                        agent_id=agent_id,
                        resource=resource,
                        action=action,
                    )

        return PolicyResult(
            allowed=False,
            reason=(
                f"No policy allows agent '{agent_id}' to perform "
                f"{action!r} on {resource!r}"
            ),
            agent_id=agent_id,
            resource=resource,
            action=action,
        )

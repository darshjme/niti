"""Exceptions for agent-policy."""


class PermissionDeniedError(Exception):
    """Raised when an agent is denied access to a resource/action."""

    def __init__(self, agent_id: str, resource: str, action: str, reason: str = ""):
        self.agent_id = agent_id
        self.resource = resource
        self.action = action
        self.reason = reason
        msg = f"Agent '{agent_id}' denied: {action} on '{resource}'"
        if reason:
            msg += f" — {reason}"
        super().__init__(msg)

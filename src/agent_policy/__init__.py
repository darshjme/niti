"""agent-policy: Policy-based access control for agent actions."""

from .permission import Permission
from .policy import Policy
from .result import PolicyResult
from .engine import PolicyEngine
from .decorator import require_permission
from .exceptions import PermissionDeniedError

__all__ = [
    "Permission",
    "Policy",
    "PolicyResult",
    "PolicyEngine",
    "require_permission",
    "PermissionDeniedError",
]

__version__ = "1.0.0"

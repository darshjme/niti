"""Comprehensive test suite for agent-policy (22+ tests)."""

import pytest

from agent_policy import (
    Permission,
    Policy,
    PolicyEngine,
    PolicyResult,
    PermissionDeniedError,
    require_permission,
)


# ---------------------------------------------------------------------------
# Permission tests
# ---------------------------------------------------------------------------

class TestPermission:
    def test_basic_match(self):
        p = Permission("db", "read")
        assert p.matches("db", "read")

    def test_no_match_resource(self):
        p = Permission("db", "read")
        assert not p.matches("api", "read")

    def test_no_match_action(self):
        p = Permission("db", "read")
        assert not p.matches("db", "write")

    def test_wildcard_resource(self):
        p = Permission("db:*", "read")
        assert p.matches("db:users", "read")
        assert p.matches("db:orders", "read")
        assert not p.matches("api:users", "read")

    def test_wildcard_action(self):
        p = Permission("api", "*")
        assert p.matches("api", "GET")
        assert p.matches("api", "POST")
        assert not p.matches("db", "read")

    def test_conditions_match(self):
        p = Permission("reports", "read", conditions={"env": "prod"})
        assert p.matches("reports", "read", context={"env": "prod"})

    def test_conditions_mismatch(self):
        p = Permission("reports", "read", conditions={"env": "prod"})
        assert not p.matches("reports", "read", context={"env": "staging"})

    def test_conditions_missing_in_context(self):
        p = Permission("reports", "read", conditions={"env": "prod"})
        assert not p.matches("reports", "read", context={})

    def test_to_dict_no_conditions(self):
        p = Permission("db", "read")
        assert p.to_dict() == {"resource": "db", "action": "read"}

    def test_to_dict_with_conditions(self):
        p = Permission("db", "read", conditions={"env": "prod"})
        d = p.to_dict()
        assert d["conditions"] == {"env": "prod"}

    def test_invalid_resource_raises(self):
        with pytest.raises(ValueError):
            Permission("", "read")

    def test_invalid_action_raises(self):
        with pytest.raises(ValueError):
            Permission("db", "")


# ---------------------------------------------------------------------------
# Policy tests
# ---------------------------------------------------------------------------

class TestPolicy:
    def test_allows_basic(self):
        policy = Policy("read-only").add_permission(Permission("db", "read"))
        assert policy.allows("db", "read")
        assert not policy.allows("db", "write")

    def test_deny_overrides_allow(self):
        policy = (
            Policy("mixed")
            .add_permission(Permission("db", "*"))
            .add_deny(Permission("db", "delete"))
        )
        assert policy.allows("db", "read")
        assert not policy.allows("db", "delete")

    def test_no_permissions_denies(self):
        policy = Policy("empty")
        assert not policy.allows("db", "read")

    def test_fluent_chaining(self):
        policy = (
            Policy("chain")
            .add_permission(Permission("a", "r"))
            .add_permission(Permission("b", "r"))
        )
        assert policy.allows("a", "r")
        assert policy.allows("b", "r")

    def test_to_dict(self):
        policy = Policy("p1").add_permission(Permission("db", "read"))
        d = policy.to_dict()
        assert d["name"] == "p1"
        assert len(d["allow"]) == 1
        assert d["deny"] == []

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError):
            Policy("")

    def test_add_permission_type_error(self):
        with pytest.raises(TypeError):
            Policy("x").add_permission("not-a-permission")  # type: ignore


# ---------------------------------------------------------------------------
# PolicyEngine tests
# ---------------------------------------------------------------------------

class TestPolicyEngine:
    def test_no_policy_denies(self):
        engine = PolicyEngine()
        result = engine.check("agent-x", "db", "read")
        assert not result.allowed
        assert "No policies" in result.reason

    def test_attach_and_allow(self):
        engine = PolicyEngine()
        policy = Policy("rw").add_permission(Permission("db", "read"))
        engine.attach("agent-a", policy)
        result = engine.check("agent-a", "db", "read")
        assert result.allowed

    def test_attach_and_deny(self):
        engine = PolicyEngine()
        policy = Policy("ro").add_permission(Permission("db", "read"))
        engine.attach("agent-a", policy)
        result = engine.check("agent-a", "db", "write")
        assert not result.allowed

    def test_explicit_deny_wins(self):
        engine = PolicyEngine()
        policy = (
            Policy("deny-delete")
            .add_permission(Permission("db", "*"))
            .add_deny(Permission("db", "delete"))
        )
        engine.attach("agent-a", policy)
        assert not engine.check("agent-a", "db", "delete").allowed
        assert engine.check("agent-a", "db", "read").allowed

    def test_detach_policy(self):
        engine = PolicyEngine()
        policy = Policy("p").add_permission(Permission("db", "read"))
        engine.attach("agent-a", policy)
        engine.detach("agent-a", "p")
        assert not engine.check("agent-a", "db", "read").allowed

    def test_policies_for(self):
        engine = PolicyEngine()
        p1 = Policy("p1").add_permission(Permission("a", "r"))
        p2 = Policy("p2").add_permission(Permission("b", "r"))
        engine.attach("agent-a", p1)
        engine.attach("agent-a", p2)
        names = {p.name for p in engine.policies_for("agent-a")}
        assert names == {"p1", "p2"}

    def test_multiple_agents_isolation(self):
        engine = PolicyEngine()
        engine.attach("agent-a", Policy("pa").add_permission(Permission("db", "read")))
        engine.attach("agent-b", Policy("pb").add_permission(Permission("api", "POST")))
        assert engine.check("agent-a", "db", "read").allowed
        assert not engine.check("agent-a", "api", "POST").allowed
        assert engine.check("agent-b", "api", "POST").allowed

    def test_result_to_dict(self):
        engine = PolicyEngine()
        engine.attach("agent-a", Policy("p").add_permission(Permission("db", "read")))
        d = engine.check("agent-a", "db", "read").to_dict()
        assert d["allowed"] is True
        assert d["agent_id"] == "agent-a"

    def test_result_bool(self):
        r = PolicyResult(allowed=True, reason="ok", agent_id="a", resource="r", action="x")
        assert bool(r) is True
        r2 = PolicyResult(allowed=False, reason="no", agent_id="a", resource="r", action="x")
        assert bool(r2) is False

    def test_attach_type_error(self):
        engine = PolicyEngine()
        with pytest.raises(TypeError):
            engine.attach("a", "not-a-policy")  # type: ignore


# ---------------------------------------------------------------------------
# @require_permission tests
# ---------------------------------------------------------------------------

class TestRequirePermission:
    def test_allowed_function_runs(self):
        engine = PolicyEngine()
        engine.attach("agent-a", Policy("p").add_permission(Permission("db", "read")))

        @require_permission(engine, "agent-a", "db", "read")
        def fetch():
            return 42

        assert fetch() == 42

    def test_denied_raises(self):
        engine = PolicyEngine()
        engine.attach("agent-a", Policy("p").add_permission(Permission("db", "read")))

        @require_permission(engine, "agent-a", "db", "write")
        def insert():
            return "inserted"

        with pytest.raises(PermissionDeniedError) as exc_info:
            insert()
        err = exc_info.value
        assert err.agent_id == "agent-a"
        assert err.resource == "db"
        assert err.action == "write"

    def test_preserves_function_name(self):
        engine = PolicyEngine()
        engine.attach("agent-a", Policy("p").add_permission(Permission("db", "read")))

        @require_permission(engine, "agent-a", "db", "read")
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

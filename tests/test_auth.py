import json
from uuid import uuid4

import pytest

from astrynn_devforge.api.auth import (
    AuthRole,
    InMemoryTokenAuthenticator,
    Permission,
    Principal,
)


def test_authenticator_matches_registered_token() -> None:
    principal = Principal(uuid4(), uuid4(), AuthRole.REVIEWER, "Reviewer")
    authenticator = InMemoryTokenAuthenticator({"secret-token": principal})

    assert authenticator.authenticate("secret-token") == principal
    assert authenticator.authenticate("wrong-token") is None


def test_role_permission_matrix_is_least_privilege() -> None:
    owner = Principal(uuid4(), uuid4(), AuthRole.CASE_OWNER)
    reviewer = Principal(uuid4(), uuid4(), AuthRole.REVIEWER)
    viewer = Principal(uuid4(), uuid4(), AuthRole.VIEWER)

    assert owner.has_permission(Permission.CASE_CREATE)
    assert not owner.has_permission(Permission.CASE_APPROVE)
    assert reviewer.has_permission(Permission.CASE_APPROVE)
    assert not reviewer.has_permission(Permission.CASE_CREATE)
    assert viewer.has_permission(Permission.CASE_READ)
    assert not viewer.has_permission(Permission.CASE_TRANSITION)


def test_environment_loader_builds_principal(monkeypatch) -> None:
    actor_id = uuid4()
    organization_id = uuid4()
    payload = [
        {
            "token": "environment-token",
            "actor_id": str(actor_id),
            "organization_id": str(organization_id),
            "role": "ORG_ADMIN",
            "display_name": "Org Admin",
        }
    ]
    monkeypatch.setenv("ASTRYNN_API_TOKENS_JSON", json.dumps(payload))

    authenticator = InMemoryTokenAuthenticator.from_environment()
    principal = authenticator.authenticate("environment-token")

    assert principal is not None
    assert principal.actor_id == actor_id
    assert principal.organization_id == organization_id
    assert principal.role is AuthRole.ORG_ADMIN


def test_invalid_environment_json_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("ASTRYNN_API_TOKENS_JSON", "not-json")

    with pytest.raises(RuntimeError, match="valid JSON"):
        InMemoryTokenAuthenticator.from_environment()


def test_empty_environment_produces_locked_api(monkeypatch) -> None:
    monkeypatch.delenv("ASTRYNN_API_TOKENS_JSON", raising=False)

    authenticator = InMemoryTokenAuthenticator.from_environment()

    assert authenticator.authenticate("anything") is None

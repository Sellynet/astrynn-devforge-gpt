from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class AuthRole(StrEnum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    CASE_OWNER = "CASE_OWNER"
    REVIEWER = "REVIEWER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


class Permission(StrEnum):
    CASE_CREATE = "CASE_CREATE"
    CASE_LIST = "CASE_LIST"
    CASE_READ = "CASE_READ"
    CASE_TRANSITION = "CASE_TRANSITION"
    CASE_APPROVE = "CASE_APPROVE"
    AEGIS_EVALUATE = "AEGIS_EVALUATE"
    AEGIS_RECORD = "AEGIS_RECORD"
    ATLAS_BUILD = "ATLAS_BUILD"
    ATLAS_RECORD = "ATLAS_RECORD"
    OAAA_CREATE = "OAAA_CREATE"
    OAAA_READ = "OAAA_READ"
    OAAA_REVISE = "OAAA_REVISE"
    OAAA_SUBMIT = "OAAA_SUBMIT"


_ROLE_PERMISSIONS: dict[AuthRole, frozenset[Permission]] = {
    AuthRole.SYSTEM_ADMIN: frozenset(Permission),
    AuthRole.ORG_ADMIN: frozenset(Permission),
    AuthRole.CASE_OWNER: frozenset(
        {
            Permission.CASE_CREATE,
            Permission.CASE_LIST,
            Permission.CASE_READ,
            Permission.CASE_TRANSITION,
            Permission.AEGIS_EVALUATE,
            Permission.ATLAS_BUILD,
            Permission.OAAA_CREATE,
            Permission.OAAA_READ,
            Permission.OAAA_REVISE,
            Permission.OAAA_SUBMIT,
        }
    ),
    AuthRole.REVIEWER: frozenset(
        {
            Permission.CASE_LIST,
            Permission.CASE_READ,
            Permission.CASE_TRANSITION,
            Permission.CASE_APPROVE,
            Permission.AEGIS_EVALUATE,
            Permission.AEGIS_RECORD,
            Permission.ATLAS_BUILD,
            Permission.ATLAS_RECORD,
            Permission.OAAA_CREATE,
            Permission.OAAA_READ,
            Permission.OAAA_REVISE,
            Permission.OAAA_SUBMIT,
        }
    ),
    AuthRole.AUDITOR: frozenset(
        {
            Permission.CASE_LIST,
            Permission.CASE_READ,
            Permission.OAAA_READ,
        }
    ),
    AuthRole.VIEWER: frozenset(
        {
            Permission.CASE_LIST,
            Permission.CASE_READ,
            Permission.OAAA_READ,
        }
    ),
}


@dataclass(frozen=True, slots=True)
class Principal:
    actor_id: UUID
    organization_id: UUID
    role: AuthRole
    display_name: str = ""

    def has_permission(self, permission: Permission) -> bool:
        return permission in _ROLE_PERMISSIONS[self.role]

    @property
    def is_system_admin(self) -> bool:
        return self.role is AuthRole.SYSTEM_ADMIN


@dataclass(frozen=True, slots=True)
class _TokenRecord:
    token_digest: bytes
    principal: Principal


class InMemoryTokenAuthenticator:
    """Development authenticator using SHA-256 token digests in memory.

    Tokens are loaded from environment configuration or injected by tests. This is a
    transitional control for the private API, not a production identity provider.
    """

    def __init__(self, token_principals: dict[str, Principal] | None = None) -> None:
        self._records = tuple(
            _TokenRecord(self._digest(token), principal)
            for token, principal in (token_principals or {}).items()
        )

    @staticmethod
    def _digest(token: str) -> bytes:
        return hashlib.sha256(token.encode("utf-8")).digest()

    @classmethod
    def from_environment(cls) -> InMemoryTokenAuthenticator:
        raw = os.getenv("ASTRYNN_API_TOKENS_JSON", "").strip()
        if not raw:
            return cls()

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("ASTRYNN_API_TOKENS_JSON must contain valid JSON") from exc

        if not isinstance(payload, list):
            # Startup configuration errors intentionally share one exception contract.
            raise RuntimeError(  # noqa: TRY004
                "ASTRYNN_API_TOKENS_JSON must be a JSON list"
            )

        records: dict[str, Principal] = {}
        for item in payload:
            if not isinstance(item, dict):
                raise RuntimeError(  # noqa: TRY004
                    "Each token record must be a JSON object"
                )
            try:
                token = str(item["token"])
                principal = Principal(
                    actor_id=UUID(str(item["actor_id"])),
                    organization_id=UUID(str(item["organization_id"])),
                    role=AuthRole(str(item["role"])),
                    display_name=str(item.get("display_name", "")),
                )
            except (KeyError, ValueError, TypeError) as exc:
                raise RuntimeError("Invalid token record in ASTRYNN_API_TOKENS_JSON") from exc
            if not token.strip():
                raise RuntimeError("API tokens cannot be empty")
            records[token] = principal

        return cls(records)

    def authenticate(self, token: str) -> Principal | None:
        candidate = self._digest(token)
        for record in self._records:
            if hmac.compare_digest(candidate, record.token_digest):
                return record.principal
        return None


_bearer = HTTPBearer(auto_error=False)


def current_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    principal = request.app.state.container.authenticator.authenticate(credentials.credentials)
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return principal


CurrentPrincipal = Annotated[Principal, Depends(current_principal)]


def require_permission(principal: Principal, permission: Permission) -> None:
    if not principal.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {principal.role.value} lacks {permission.value}",
        )


def require_organization_access(principal: Principal, organization_id: UUID) -> None:
    if principal.is_system_admin:
        return
    if principal.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-organization access is not allowed",
        )

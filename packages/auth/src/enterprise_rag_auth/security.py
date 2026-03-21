from __future__ import annotations

from collections.abc import Sequence

import jwt
from enterprise_rag_core.settings import get_settings
from fastapi import HTTPException, status
from jwt import InvalidTokenError

from enterprise_rag_auth.principal import Principal


def _normalize_claim_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        items: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise _unauthorized("JWT group or role claim must contain strings.")
            normalized = item.strip()
            if normalized:
                items.append(normalized)
        return items
    raise _unauthorized("JWT group or role claim must be a list or comma-delimited string.")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def decode_jwt_token(token: str) -> Principal:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise _unauthorized("Invalid authentication token.") from exc

    user_id = payload.get("user_id")
    tenant_id = payload.get("tenant_id")
    if not isinstance(user_id, str) or not user_id:
        raise _unauthorized("JWT is missing a valid user_id claim.")
    if not isinstance(tenant_id, str) or not tenant_id:
        raise _unauthorized("JWT is missing a valid tenant_id claim.")

    return Principal(
        user_id=user_id,
        tenant_id=tenant_id,
        groups=_normalize_claim_list(payload.get("groups")),
        roles=_normalize_claim_list(payload.get("roles")),
    )

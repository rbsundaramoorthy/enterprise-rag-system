from __future__ import annotations

from typing import Annotated

from enterprise_rag_auth.principal import Principal
from enterprise_rag_auth.security import decode_jwt_token
from enterprise_rag_core.db import get_db_session
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from enterprise_rag_api.request_context import RequestContext

bearer_scheme = HTTPBearer(auto_error=False)


def get_request_context(request: Request) -> RequestContext:
    context = getattr(request.state, "context", None)
    if not isinstance(context, RequestContext):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request context is unavailable.",
        )
    return context


def get_current_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> Principal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    principal = decode_jwt_token(credentials.credentials)
    context = get_request_context(request)
    context.principal = principal
    return principal


def enforce_tenant_access(tenant_id: str, principal: Principal) -> None:
    if principal.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access is forbidden.",
        )


DbSession = Annotated[Session, Depends(get_db_session)]
CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]

from __future__ import annotations

from dataclasses import dataclass

from enterprise_rag_auth.principal import Principal


@dataclass
class RequestContext:
    correlation_id: str
    principal: Principal | None = None

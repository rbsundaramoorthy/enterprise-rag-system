from __future__ import annotations

from pydantic import BaseModel, Field


class Principal(BaseModel):
    user_id: str
    tenant_id: str
    groups: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)

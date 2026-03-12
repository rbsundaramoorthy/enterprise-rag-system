from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str


class UserPrincipal(BaseModel):
    tenant_id: UUID
    user_id: str
    group_ids: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)


class ACL(BaseModel):
    allow_users: list[str] = Field(default_factory=list)
    allow_groups: list[str] = Field(default_factory=list)
    allow_roles: list[str] = Field(default_factory=list)
    deny_users: list[str] = Field(default_factory=list)
    deny_groups: list[str] = Field(default_factory=list)
    deny_roles: list[str] = Field(default_factory=list)


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    title: str
    content: str
    acl: ACL = Field(default_factory=ACL)
    metadata: dict[str, str] = Field(default_factory=dict)


class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    tenant_id: UUID
    text: str
    sequence_number: int
    acl: ACL = Field(default_factory=ACL)


class IndexEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    document_id: UUID
    operation: Literal["upsert", "delete"]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


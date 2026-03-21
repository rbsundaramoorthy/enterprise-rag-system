from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MeResponse(BaseModel):
    user_id: str
    tenant_id: str
    groups: list[str]
    roles: list[str]
    correlation_id: str


class DocumentListItem(BaseModel):
    id: str
    tenant_id: str
    title: str
    source_type: str
    mime_type: str | None
    tags: list[str]
    status: str
    created_by_user_id: str
    source_uri: str | None
    created_at: datetime


class IngestionAcceptedResponse(BaseModel):
    ingestion_job_id: str
    document_id: str
    status: str


class IngestionJobResponse(BaseModel):
    id: str
    tenant_id: str
    document_id: str | None
    source_uri: str | None
    source_type: str
    status: str
    created_at: datetime
    updated_at: datetime

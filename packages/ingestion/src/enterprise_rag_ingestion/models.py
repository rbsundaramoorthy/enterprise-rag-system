from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class ACLInput(BaseModel):
    allowed_users: list[str] = Field(default_factory=list)
    allowed_groups: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=list)


class DocumentMetadataInput(BaseModel):
    title: str
    tags: list[str] = Field(default_factory=list)


class TextIngestionRequest(DocumentMetadataInput):
    content: str
    acl: ACLInput = Field(default_factory=ACLInput)


class URLIngestionRequest(DocumentMetadataInput):
    url: HttpUrl
    acl: ACLInput = Field(default_factory=ACLInput)


class ParsedContent(BaseModel):
    text: str
    mime_type: str


class EventEnvelope(BaseModel):
    event_type: str
    tenant_id: str
    document_id: str
    document_version_id: str
    ingestion_job_id: str
    payload: dict[str, str | list[str]]

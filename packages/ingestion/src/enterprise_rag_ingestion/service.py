from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from enterprise_rag_auth.principal import Principal
from enterprise_rag_core.db_models import (
    ACLEntryRecord,
    DocumentRecord,
    DocumentVersionRecord,
    IndexEventRecord,
    IngestionJobRecord,
)
from sqlalchemy.orm import Session

from enterprise_rag_ingestion.events import EventPublisher, RedisStreamEventPublisher
from enterprise_rag_ingestion.models import ACLInput, EventEnvelope
from enterprise_rag_ingestion.parsers import BasicParser, Parser
from enterprise_rag_ingestion.storage import LocalRawContentStore


def utc_now() -> datetime:
    return datetime.now(UTC)


class IngestionService:
    def __init__(
        self,
        *,
        parser: Parser | None = None,
        raw_store: LocalRawContentStore | None = None,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._parser = parser or BasicParser()
        self._raw_store = raw_store or LocalRawContentStore()
        self._publisher = publisher or RedisStreamEventPublisher()

    def ingest_text(
        self,
        *,
        db: Session,
        principal: Principal,
        title: str,
        content: str,
        tags: list[str],
        acl: ACLInput,
    ) -> IngestionJobRecord:
        raw_bytes = content.encode("utf-8")
        parsed = self._parser.parse(raw_bytes, "text/plain")
        return self._persist_ingestion(
            db=db,
            principal=principal,
            title=title,
            source_type="text",
            source_uri=None,
            mime_type=parsed.mime_type,
            raw_filename="document.txt",
            raw_content=raw_bytes,
            extracted_text=parsed.text,
            tags=tags,
            acl=acl,
        )

    def ingest_upload(
        self,
        *,
        db: Session,
        principal: Principal,
        title: str,
        filename: str,
        mime_type: str,
        raw_content: bytes,
        tags: list[str],
        acl: ACLInput,
    ) -> IngestionJobRecord:
        parsed = self._parser.parse(raw_content, mime_type)
        safe_filename = Path(filename).name or "upload.bin"
        return self._persist_ingestion(
            db=db,
            principal=principal,
            title=title,
            source_type="upload",
            source_uri=None,
            mime_type=parsed.mime_type,
            raw_filename=safe_filename,
            raw_content=raw_content,
            extracted_text=parsed.text,
            tags=tags,
            acl=acl,
        )

    def ingest_url(
        self,
        *,
        db: Session,
        principal: Principal,
        title: str,
        url: str,
        tags: list[str],
        acl: ACLInput,
    ) -> IngestionJobRecord:
        return self._persist_ingestion(
            db=db,
            principal=principal,
            title=title,
            source_type="url",
            source_uri=url,
            mime_type="text/html",
            raw_filename="source.url",
            raw_content=url.encode("utf-8"),
            extracted_text=f"URL ingestion queued for {url}",
            tags=tags,
            acl=acl,
        )

    def _persist_ingestion(
        self,
        *,
        db: Session,
        principal: Principal,
        title: str,
        source_type: str,
        source_uri: str | None,
        mime_type: str,
        raw_filename: str,
        raw_content: bytes,
        extracted_text: str,
        tags: list[str],
        acl: ACLInput,
    ) -> IngestionJobRecord:
        now = utc_now()
        document = DocumentRecord(
            tenant_id=principal.tenant_id,
            created_by_user_id=principal.user_id,
            title=title,
            source_uri=source_uri,
            source_type=source_type,
            mime_type=mime_type,
            tags=tags,
            status="pending_index",
            created_at=now,
            updated_at=now,
        )
        db.add(document)
        db.flush()

        raw_path = self._raw_store.write_bytes(
            tenant_id=principal.tenant_id,
            document_id=document.id,
            version=1,
            filename=raw_filename,
            content=raw_content,
        )

        version = DocumentVersionRecord(
            tenant_id=principal.tenant_id,
            document_id=document.id,
            version_number=1,
            content=extracted_text,
            source_uri=raw_path,
            created_at=now,
            updated_at=now,
        )
        db.add(version)
        db.flush()

        job = IngestionJobRecord(
            tenant_id=principal.tenant_id,
            document_id=document.id,
            source_uri=source_uri or raw_path,
            source_type=source_type,
            status="queued",
            created_at=now,
            updated_at=now,
        )
        db.add(job)
        db.flush()

        self._store_acl_entries(
            db=db,
            tenant_id=principal.tenant_id,
            document_id=document.id,
            acl=acl,
        )

        event_payload = EventEnvelope(
            event_type="document.created",
            tenant_id=principal.tenant_id,
            document_id=document.id,
            document_version_id=version.id,
            ingestion_job_id=job.id,
            payload={
                "title": title,
                "source_type": source_type,
                "mime_type": mime_type,
                "tags": tags,
            },
        )
        stream_message_id = self._publisher.publish(event_payload)

        db.add(
            IndexEventRecord(
                tenant_id=principal.tenant_id,
                document_id=document.id,
                document_version_id=version.id,
                event_type=event_payload.event_type,
                status="published",
                payload={
                    **event_payload.payload,
                    "stream": f"idx:events:{principal.tenant_id}",
                    "stream_message_id": stream_message_id,
                    "ingestion_job_id": job.id,
                },
                attempt_count=0,
                created_at=now,
            )
        )
        db.commit()
        db.refresh(job)
        return job

    def _store_acl_entries(
        self,
        *,
        db: Session,
        tenant_id: str,
        document_id: str,
        acl: ACLInput,
    ) -> None:
        for subject_type, subject_ids in (
            ("user", acl.allowed_users),
            ("group", acl.allowed_groups),
            ("role", acl.allowed_roles),
        ):
            for subject_id in subject_ids:
                db.add(
                    ACLEntryRecord(
                        tenant_id=tenant_id,
                        document_id=document_id,
                        subject_type=subject_type,
                        subject_id=subject_id,
                        effect="allow",
                    )
                )

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from enterprise_rag_api.ingestion_dependencies import get_ingestion_service
from enterprise_rag_api.main import create_app
from enterprise_rag_core.db import get_engine, get_session_factory, reset_db_state
from enterprise_rag_core.db_models import (
    ACLEntryRecord,
    Base,
    DocumentRecord,
    DocumentVersionRecord,
    GroupMembershipRecord,
    GroupRecord,
    IndexEventRecord,
    IngestionJobRecord,
    TenantRecord,
    UserRecord,
)
from enterprise_rag_core.settings import clear_settings_cache, get_settings
from enterprise_rag_ingestion.service import IngestionService
from enterprise_rag_ingestion.storage import LocalRawContentStore
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.support import InMemoryEventPublisher


@pytest.fixture
def test_app(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, InMemoryEventPublisher, Path]]:
    database_path = tmp_path / "test.db"
    raw_storage_path = tmp_path / "raw"
    monkeypatch.setenv("ENTERPRISE_RAG_DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("ENTERPRISE_RAG_JWT_SECRET", "test-secret-32-bytes-minimum-key")
    monkeypatch.setenv("ENTERPRISE_RAG_RAW_STORAGE_ROOT", str(raw_storage_path))

    clear_settings_cache()
    reset_db_state()

    settings = get_settings()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    session = get_session_factory()()
    try:
        tenant_a = TenantRecord(id="tenant-acme", name="Acme Corp")
        tenant_b = TenantRecord(id="tenant-globex", name="Globex Corp")
        user_a = UserRecord(
            id="user-acme-1",
            tenant_id=tenant_a.id,
            email="alice@acme.test",
            display_name="Alice",
        )
        user_b = UserRecord(
            id="user-globex-1",
            tenant_id=tenant_b.id,
            email="carol@globex.test",
            display_name="Carol",
        )
        group_a = GroupRecord(id="group-acme-eng", tenant_id=tenant_a.id, name="engineering")
        membership = GroupMembershipRecord(user_id=user_a.id, group_id=group_a.id)
        document_a = DocumentRecord(
            id="doc-acme-1",
            tenant_id=tenant_a.id,
            created_by_user_id=user_a.id,
            title="Acme Handbook",
            source_uri="file://acme.pdf",
            source_type="upload",
            mime_type="text/plain",
            tags=["handbook"],
            updated_at=tenant_a.created_at,
        )
        document_b = DocumentRecord(
            id="doc-globex-1",
            tenant_id=tenant_b.id,
            created_by_user_id=user_b.id,
            title="Globex Playbook",
            source_uri="file://globex.pdf",
            source_type="upload",
            mime_type="text/plain",
            tags=["legal"],
            updated_at=tenant_b.created_at,
        )
        version_a = DocumentVersionRecord(
            id="doc-acme-v1",
            tenant_id=tenant_a.id,
            document_id=document_a.id,
            version_number=1,
            content="Acme handbook content",
            source_uri="file://acme.pdf",
            updated_at=tenant_a.created_at,
        )
        job_a = IngestionJobRecord(
            id="job-acme-1",
            tenant_id=tenant_a.id,
            document_id=document_a.id,
            source_uri="file://acme.pdf",
            source_type="upload",
            status="queued",
            created_at=tenant_a.created_at,
            updated_at=tenant_a.created_at,
        )
        acl_entry = ACLEntryRecord(
            id="acl-acme-1",
            tenant_id=tenant_a.id,
            document_id=document_a.id,
            subject_type="group",
            subject_id="engineering",
            effect="allow",
        )
        index_event = IndexEventRecord(
            id="evt-acme-1",
            tenant_id=tenant_a.id,
            document_id=document_a.id,
            document_version_id=version_a.id,
            event_type="document.created",
            status="published",
            payload={"stream": "idx:events:tenant-acme"},
            attempt_count=0,
            created_at=tenant_a.created_at,
        )
        session.add_all(
            [
                tenant_a,
                tenant_b,
                user_a,
                user_b,
                group_a,
                membership,
                document_a,
                document_b,
                version_a,
                job_a,
                acl_entry,
                index_event,
            ]
        )
        session.commit()
    finally:
        session.close()

    app: FastAPI = create_app(settings)
    client = TestClient(app)
    publisher = InMemoryEventPublisher()
    app.dependency_overrides[get_ingestion_service] = lambda: IngestionService(
        raw_store=LocalRawContentStore(raw_storage_path),
        publisher=publisher,
    )
    try:
        yield client, publisher, raw_storage_path
    finally:
        client.close()
        app.dependency_overrides.clear()
        clear_settings_cache()
        reset_db_state()

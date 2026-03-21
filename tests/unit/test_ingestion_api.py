from __future__ import annotations

from pathlib import Path

from enterprise_rag_core.db import get_session_factory
from enterprise_rag_core.db_models import ACLEntryRecord, DocumentRecord, IngestionJobRecord
from fastapi.testclient import TestClient
from sqlalchemy import select

from tests.support import InMemoryEventPublisher, make_token


def test_text_ingestion_creates_rows_event_and_raw_file(
    test_app: tuple[TestClient, InMemoryEventPublisher, Path],
) -> None:
    client, publisher, raw_storage_path = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.post(
        "/v1/documents/text",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Quarterly Notes",
            "content": "Revenue increased.",
            "tags": ["finance", "q1"],
            "acl": {
                "allowed_users": ["user-acme-1"],
                "allowed_groups": ["engineering"],
                "allowed_roles": ["member"],
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert len(publisher.events) == 1
    assert publisher.events[0].tenant_id == "tenant-acme"

    session = get_session_factory()()
    try:
        job = session.get(IngestionJobRecord, body["ingestion_job_id"])
        assert job is not None
        assert job.source_type == "text"

        document = session.get(DocumentRecord, body["document_id"])
        assert document is not None
        assert document.tags == ["finance", "q1"]
        assert document.mime_type == "text/plain"
        expected_path = raw_storage_path / "tenant-acme" / document.id / "1" / "document.txt"
        assert expected_path.exists()
        acl_entries = session.scalars(
            select(ACLEntryRecord).where(ACLEntryRecord.document_id == document.id)
        ).all()
        assert {(entry.subject_type, entry.subject_id) for entry in acl_entries} == {
            ("user", "user-acme-1"),
            ("group", "engineering"),
            ("role", "member"),
        }
    finally:
        session.close()


def test_upload_ingestion_accepts_text_files(
    test_app: tuple[TestClient, InMemoryEventPublisher, Path],
) -> None:
    client, publisher, raw_storage_path = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.post(
        "/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "title": "Upload Doc",
            "tags": "alpha,beta",
            "allowed_groups": "engineering",
        },
        files={"file": ("upload.txt", b"plain upload body", "text/plain")},
    )

    assert response.status_code == 201
    assert len(publisher.events) == 1

    session = get_session_factory()()
    try:
        document = session.get(DocumentRecord, response.json()["document_id"])
        assert document is not None
        assert document.source_type == "upload"
        assert document.tags == ["alpha", "beta"]
        expected_path = raw_storage_path / "tenant-acme" / document.id / "1" / "upload.txt"
        assert expected_path.read_text() == "plain upload body"
    finally:
        session.close()


def test_get_ingestion_job_enforces_tenant_ownership(
    test_app: tuple[TestClient, InMemoryEventPublisher, Path],
) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-globex-1",
        tenant_id="tenant-globex",
        groups=["legal"],
        roles=["member"],
    )

    response = client.get(
        "/v1/ingestion-jobs/job-acme-1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Cross-tenant access is forbidden."}


def test_get_ingestion_job_returns_job_for_owner(
    test_app: tuple[TestClient, InMemoryEventPublisher, Path],
) -> None:
    client, _, _ = test_app
    token = make_token(
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        groups=["engineering"],
        roles=["member"],
    )

    response = client.get(
        "/v1/ingestion-jobs/job-acme-1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "job-acme-1"
    assert response.json()["tenant_id"] == "tenant-acme"

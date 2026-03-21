from __future__ import annotations

from enterprise_rag_core.db import get_session_factory
from enterprise_rag_core.db_models import (
    ACLEntryRecord,
    DocumentRecord,
    DocumentVersionRecord,
    GroupMembershipRecord,
    GroupRecord,
    TenantRecord,
    UserRecord,
    create_all_tables,
)


def seed_data() -> None:
    create_all_tables()
    session = get_session_factory()()
    try:
        if session.query(TenantRecord).count() > 0:
            return

        tenant_a = TenantRecord(name="Acme Corp")
        tenant_b = TenantRecord(name="Globex Corp")
        session.add_all([tenant_a, tenant_b])
        session.flush()

        users = [
            UserRecord(
                tenant_id=tenant_a.id,
                email="alice@acme.test",
                display_name="Alice",
            ),
            UserRecord(
                tenant_id=tenant_a.id,
                email="bob@acme.test",
                display_name="Bob",
            ),
            UserRecord(
                tenant_id=tenant_b.id,
                email="carol@globex.test",
                display_name="Carol",
            ),
            UserRecord(
                tenant_id=tenant_b.id,
                email="dave@globex.test",
                display_name="Dave",
            ),
        ]
        session.add_all(users)
        session.flush()

        acme_group = GroupRecord(tenant_id=tenant_a.id, name="engineering")
        globex_group = GroupRecord(tenant_id=tenant_b.id, name="legal")
        session.add_all([acme_group, globex_group])
        session.flush()

        session.add_all(
            [
                GroupMembershipRecord(user_id=users[0].id, group_id=acme_group.id),
                GroupMembershipRecord(user_id=users[2].id, group_id=globex_group.id),
            ]
        )

        acme_doc = DocumentRecord(
            tenant_id=tenant_a.id,
            created_by_user_id=users[0].id,
            title="Acme Employee Handbook",
            source_uri="file://docs/acme-handbook.pdf",
            source_type="upload",
            mime_type="application/pdf",
            tags=["handbook", "hr"],
            updated_at=tenant_a.created_at,
        )
        globex_doc = DocumentRecord(
            tenant_id=tenant_b.id,
            created_by_user_id=users[2].id,
            title="Globex Legal Playbook",
            source_uri="file://docs/globex-legal.pdf",
            source_type="upload",
            mime_type="application/pdf",
            tags=["legal"],
            updated_at=tenant_b.created_at,
        )
        session.add_all([acme_doc, globex_doc])
        session.flush()

        session.add_all(
            [
                DocumentVersionRecord(
                    tenant_id=tenant_a.id,
                    document_id=acme_doc.id,
                    version_number=1,
                    content="Welcome to Acme.",
                    source_uri="file://docs/acme-handbook.pdf",
                    updated_at=tenant_a.created_at,
                ),
                DocumentVersionRecord(
                    tenant_id=tenant_b.id,
                    document_id=globex_doc.id,
                    version_number=1,
                    content="Globex legal guidance.",
                    source_uri="file://docs/globex-legal.pdf",
                    updated_at=tenant_b.created_at,
                ),
            ]
        )

        session.add_all(
            [
                ACLEntryRecord(
                    tenant_id=tenant_a.id,
                    document_id=acme_doc.id,
                    subject_type="group",
                    subject_id="engineering",
                    effect="allow",
                ),
                ACLEntryRecord(
                    tenant_id=tenant_b.id,
                    document_id=globex_doc.id,
                    subject_type="role",
                    subject_id="legal-reviewer",
                    effect="allow",
                ),
            ]
        )

        session.commit()
    finally:
        session.close()


def main() -> None:
    seed_data()
    print("Seeded Phase 01 sample data.")

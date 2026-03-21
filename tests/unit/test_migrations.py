from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from enterprise_rag_core.db import reset_db_state
from enterprise_rag_core.settings import clear_settings_cache
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_creates_phase_01_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "migration.db"
    monkeypatch.setenv("ENTERPRISE_RAG_DATABASE_URL", f"sqlite:///{database_path}")
    clear_settings_cache()
    reset_db_state()

    config = Config("alembic.ini")
    config.set_main_option(
        "script_location",
        str(Path("infra/migrations").resolve()),
    )

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{database_path}")
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) >= {
        "acl_entries",
        "chunks",
        "document_versions",
        "documents",
        "group_memberships",
        "groups",
        "index_events",
        "ingestion_jobs",
        "tenants",
        "users",
    }
    document_columns = {column["name"] for column in inspector.get_columns("documents")}
    assert {"source_type", "mime_type", "tags", "updated_at"} <= document_columns
    ingestion_job_columns = {column["name"] for column in inspector.get_columns("ingestion_jobs")}
    assert {"source_type"} <= ingestion_job_columns

    clear_settings_cache()
    reset_db_state()

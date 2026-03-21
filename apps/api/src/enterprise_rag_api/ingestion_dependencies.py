from __future__ import annotations

from enterprise_rag_ingestion.service import IngestionService


def get_ingestion_service() -> IngestionService:
    return IngestionService()

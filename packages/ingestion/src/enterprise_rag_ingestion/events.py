from __future__ import annotations

from abc import ABC, abstractmethod

from enterprise_rag_core.settings import get_settings
from redis import Redis

from enterprise_rag_ingestion.models import EventEnvelope


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, envelope: EventEnvelope) -> str:
        raise NotImplementedError


class RedisStreamEventPublisher(EventPublisher):
    def __init__(self, client: Redis | None = None) -> None:
        settings = get_settings()
        self._client = client or Redis.from_url(settings.redis_dsn, decode_responses=True)

    def publish(self, envelope: EventEnvelope) -> str:
        stream_name = f"idx:events:{envelope.tenant_id}"
        return str(
            self._client.xadd(
                stream_name,
                {
                    "event_type": envelope.event_type,
                    "tenant_id": envelope.tenant_id,
                    "document_id": envelope.document_id,
                    "document_version_id": envelope.document_version_id,
                    "ingestion_job_id": envelope.ingestion_job_id,
                    "payload": envelope.model_dump_json(),
                },
            )
        )

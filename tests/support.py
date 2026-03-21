from __future__ import annotations

import jwt
from enterprise_rag_ingestion.events import EventPublisher
from enterprise_rag_ingestion.models import EventEnvelope


class InMemoryEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    def publish(self, envelope: EventEnvelope) -> str:
        self.events.append(envelope)
        return f"{envelope.tenant_id}-1"


def make_token(*, user_id: str, tenant_id: str, groups: object, roles: object) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "groups": groups,
            "roles": roles,
        },
        "test-secret-32-bytes-minimum-key",
        algorithm="HS256",
    )

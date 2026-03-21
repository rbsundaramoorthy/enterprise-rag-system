from typing import Annotated

from enterprise_rag_core.db_models import DocumentRecord, IngestionJobRecord
from enterprise_rag_core.settings import Settings, get_settings
from enterprise_rag_ingestion.models import ACLInput, TextIngestionRequest, URLIngestionRequest
from enterprise_rag_ingestion.service import IngestionService
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select

from enterprise_rag_api.dependencies import (
    CurrentPrincipal,
    DbSession,
    enforce_tenant_access,
    get_request_context,
)
from enterprise_rag_api.ingestion_dependencies import get_ingestion_service
from enterprise_rag_api.middleware import RequestContextMiddleware
from enterprise_rag_api.schemas import (
    DocumentListItem,
    IngestionAcceptedResponse,
    IngestionJobResponse,
    MeResponse,
)

upload_file = File(...)
upload_title = Form(...)
upload_tags = Form("")
upload_allowed_users = Form("")
upload_allowed_groups = Form("")
upload_allowed_roles = Form("")


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title=app_settings.app_name)
    app.add_middleware(RequestContextMiddleware)

    ingestion_dependency = Annotated[IngestionService, Depends(get_ingestion_service)]

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/me", response_model=MeResponse)
    async def me(request: Request, principal: CurrentPrincipal) -> MeResponse:
        context = get_request_context(request)
        return MeResponse(
            user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            groups=principal.groups,
            roles=principal.roles,
            correlation_id=context.correlation_id,
        )

    @app.get(
        "/v1/tenants/{tenant_id}/documents",
        response_model=list[DocumentListItem],
    )
    async def list_documents(
        tenant_id: str,
        principal: CurrentPrincipal,
        db: DbSession,
    ) -> list[DocumentListItem]:
        enforce_tenant_access(tenant_id, principal)
        documents = db.scalars(
            select(DocumentRecord)
            .where(DocumentRecord.tenant_id == tenant_id)
            .order_by(DocumentRecord.created_at.desc())
        ).all()
        return [
            DocumentListItem(
                id=document.id,
                tenant_id=document.tenant_id,
                title=document.title,
                source_type=document.source_type,
                mime_type=document.mime_type,
                tags=document.tags,
                status=document.status,
                created_by_user_id=document.created_by_user_id,
                source_uri=document.source_uri,
                created_at=document.created_at,
            )
            for document in documents
        ]

    @app.post("/v1/documents/text", response_model=IngestionAcceptedResponse, status_code=201)
    async def ingest_text(
        payload: TextIngestionRequest,
        principal: CurrentPrincipal,
        db: DbSession,
        ingestion_service: ingestion_dependency,
    ) -> IngestionAcceptedResponse:
        job = ingestion_service.ingest_text(
            db=db,
            principal=principal,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            acl=payload.acl,
        )
        return IngestionAcceptedResponse(
            ingestion_job_id=job.id,
            document_id=job.document_id or "",
            status=job.status,
        )

    @app.post("/v1/documents/url", response_model=IngestionAcceptedResponse, status_code=201)
    async def ingest_url(
        payload: URLIngestionRequest,
        principal: CurrentPrincipal,
        db: DbSession,
        ingestion_service: ingestion_dependency,
    ) -> IngestionAcceptedResponse:
        job = ingestion_service.ingest_url(
            db=db,
            principal=principal,
            title=payload.title,
            url=str(payload.url),
            tags=payload.tags,
            acl=payload.acl,
        )
        return IngestionAcceptedResponse(
            ingestion_job_id=job.id,
            document_id=job.document_id or "",
            status=job.status,
        )

    @app.post("/v1/documents/upload", response_model=IngestionAcceptedResponse, status_code=201)
    async def ingest_upload(
        principal: CurrentPrincipal,
        db: DbSession,
        ingestion_service: ingestion_dependency,
        file: UploadFile = upload_file,
        title: str = upload_title,
        tags: str = upload_tags,
        allowed_users: str = upload_allowed_users,
        allowed_groups: str = upload_allowed_groups,
        allowed_roles: str = upload_allowed_roles,
    ) -> IngestionAcceptedResponse:
        if file.content_type not in {"text/plain", "text/html", "application/pdf"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported upload mime type.",
            )

        job = ingestion_service.ingest_upload(
            db=db,
            principal=principal,
            title=title,
            filename=file.filename or "upload.bin",
            mime_type=file.content_type,
            raw_content=await file.read(),
            tags=_split_csv(tags),
            acl=ACLInput(
                allowed_users=_split_csv(allowed_users),
                allowed_groups=_split_csv(allowed_groups),
                allowed_roles=_split_csv(allowed_roles),
            ),
        )
        return IngestionAcceptedResponse(
            ingestion_job_id=job.id,
            document_id=job.document_id or "",
            status=job.status,
        )

    @app.get("/v1/ingestion-jobs/{job_id}", response_model=IngestionJobResponse)
    async def get_ingestion_job(
        job_id: str,
        principal: CurrentPrincipal,
        db: DbSession,
    ) -> IngestionJobResponse:
        job = db.scalar(select(IngestionJobRecord).where(IngestionJobRecord.id == job_id))
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        enforce_tenant_access(job.tenant_id, principal)
        return IngestionJobResponse(
            id=job.id,
            tenant_id=job.tenant_id,
            document_id=job.document_id,
            source_uri=job.source_uri,
            source_type=job.source_type,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    return app


app = create_app()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]

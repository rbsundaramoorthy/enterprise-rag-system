# CODEX_TASK_02.md

## Phase
Phase 02 — Ingestion API

## Objective
Accept tenant-scoped content ingestion requests and publish indexing events.

## Scope
- Build the first ingestion endpoints, local content storage, ingestion job tracking, and event publishing.

## Requirements
- Implement APIs: `POST /v1/documents/upload`, `POST /v1/documents/text`, `POST /v1/documents/url`, `GET /v1/ingestion-jobs/{job_id}`
- Accept tenant-scoped uploads
- Store raw content locally in development
- Create document and document_version records
- Persist metadata: title, source_type, mime_type, created_at, updated_at, tags
- Accept ACL payload on ingestion: allowed_users, allowed_groups, allowed_roles
- Create ingestion job record
- Publish an indexing event to Redis Streams
- Return ingestion job id
- Add parser abstraction
- Add text extractor abstraction
- Add basic text/html/pdf parsing interface
- URL ingestion can be stubbed initially

## Definition of Done
- document upload or text ingestion creates DB rows and an event
- ingestion jobs are queryable
- tests, lint, and typecheck pass

## Deliverables
- first real ingest path
- event production contract from API to stream
- job status tracking

## Guardrails

```text
Implementation guardrails:
- Keep changes incremental and reviewable
- Do not introduce breaking changes to previous phases
- Add tests for all new behavior
- Prefer interfaces/abstractions at integration boundaries
- Keep security-sensitive code easy to audit
- Update README and architecture docs
- After coding, run:
  ruff check .
  mypy .
  pytest
- Then summarize:
  1. what changed
  2. why
  3. risks / follow-up work
```

## Prompt for Codex

```text
Build document ingestion APIs for the first connectors.

Implement:
- POST /v1/documents/upload
- POST /v1/documents/text
- POST /v1/documents/url (stub parser is fine initially)
- GET /v1/ingestion-jobs/{job_id}

Behavior:
- Accept tenant-scoped uploads
- Store raw content locally in dev
- Create document + version records
- Persist metadata:
  title, source_type, mime_type, created_at, updated_at, tags
- Accept ACL payload on ingestion:
  allowed_users, allowed_groups, allowed_roles
- Create ingestion job record
- Publish an indexing event to Redis Streams
- Return ingestion job id

Add:
- parser abstraction
- text extractor abstraction
- basic PDF/text/html parsing interface
- tests for file upload, text ingestion, and tenant ownership

Do not implement actual chunking or embeddings yet.
```

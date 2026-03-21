# CODEX_TASK_01.md

## Phase
Phase 01 — Data Model + Auth Context

## Objective
Establish the initial multi-tenant persistence model and request identity context.

## Scope
- Build the core SQLAlchemy schema, Alembic migrations, JWT principal extraction, and basic tenant-safe API access.

## Requirements
- Add SQLAlchemy models and Alembic migrations for tenants, users, groups, group_memberships, documents, document_versions, chunks, acl_entries, ingestion_jobs, index_events
- Add JWT auth middleware or dependency layer that extracts user_id, tenant_id, groups, roles
- Add request context middleware with correlation_id and request-scoped principal context
- Add seed script to create 2 tenants, 4 users, sample groups, sample ACL stubs
- Expose `GET /me`
- Expose `GET /v1/tenants/{tenant_id}/documents`
- Enforce tenant isolation and rejection of unauthorized access to another tenant’s resources

## Definition of Done
- every request has principal context
- migrations run successfully
- cross-tenant document listing is blocked
- tests, lint, and typecheck pass

## Deliverables
- initial DB schema
- auth principal extraction
- seed data
- first tenant-aware protected endpoints

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
Add the initial multi-tenant data model and auth plumbing.

Requirements:
- SQLAlchemy models and Alembic migrations
- Tables:
  tenants
  users
  groups
  group_memberships
  documents
  document_versions
  chunks
  acl_entries
  ingestion_jobs
  index_events
- JWT auth middleware or dependency
- Extract:
  user_id
  tenant_id
  groups
  roles
- Add request context middleware with correlation_id
- Add seed script to create:
  2 tenants
  4 users
  sample groups
  sample ACL stubs

Expose:
- GET /me
- GET /v1/tenants/{tenant_id}/documents

Enforce strict tenant isolation.

Add integration tests for:
- tenant isolation
- group claim parsing
- unauthorized access rejection
- /me response

Run tests and keep the repo runnable.
```

# Phase 01 Architecture

## Scope

Phase 01 introduces synchronous SQLAlchemy persistence, Alembic migrations, HS256 JWT principal extraction, request-scoped correlation IDs, and the first tenant-protected API endpoints.

## Runtime components

- `packages/core`: SQLAlchemy engine/session setup and the initial relational schema.
- `packages/auth`: JWT decoding and principal normalization.
- `apps/api`: request context middleware, `/me`, and tenant-scoped document listing.
- `infra/migrations`: Alembic environment and the first schema migration.

## Boundaries

ACL evaluation is not yet enforced beyond strict tenant isolation. Retrieval, indexing workers, vector search, and answer generation remain later-phase work.

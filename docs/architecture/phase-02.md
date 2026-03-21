# Phase 02 Architecture

## Scope

Phase 02 adds the first ingestion path: tenant-scoped upload, text, and URL ingestion endpoints, local raw-content storage, ingestion job tracking, and Redis Streams event publication for downstream indexing.

## Runtime components

- `packages/ingestion`: parser abstractions, local raw-content storage, event publishing, and ingestion orchestration.
- `apps/api`: ingestion APIs and job lookup endpoint.
- `packages/core`: schema extensions for ingestion metadata and job tracking.
- `infra/migrations`: Phase 02 migration for source metadata and version storage references.

## Boundaries

Chunking, embeddings, remote URL fetch, and real PDF extraction are still deferred. Phase 02 only establishes the ingestion contract and async indexing handoff.

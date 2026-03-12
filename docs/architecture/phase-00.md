# Phase 00 Architecture

## Scope

Phase 00 establishes the repository structure, base tooling, and local developer workflow for the enterprise RAG platform.

## Runtime components

- `apps/api`: FastAPI service with a `/health` endpoint.
- `apps/worker`: background worker placeholder that loads shared configuration.
- `apps/indexer`: placeholder package for future indexing flows.
- `packages/core`: shared configuration and domain models.

## Boundaries

Later phases will add persistence, eventing, ingestion, retrieval, ACL enforcement, observability, and evaluation. None of those behaviors are implemented here beyond placeholder package boundaries.


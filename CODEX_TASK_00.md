# CODEX_TASK_00.md

## Phase
Phase 00 — Monorepo Scaffold

## Objective
Initialize the monorepo scaffold for the enterprise multi-tenant RAG platform.

## Scope
- Only implement Phase 00.
- Do not implement later phases yet.

## Requirements
- Create `apps/api` for FastAPI service
- Create `apps/worker` for background worker skeleton
- Create `apps/indexer` placeholder if useful
- Create `packages/core`
- Create `packages/auth`
- Create `packages/ingestion`
- Create `packages/retrieval`
- Create `packages/llm`
- Create `packages/observability`
- Create `packages/evals`
- Create `tests`
- Create `infra/compose`
- Create `infra/migrations`
- Create `docs/architecture`
- Set up `pyproject.toml`
- Set up ruff, mypy, pytest, pre-commit
- Add Dockerfiles
- Add `docker-compose.yml` for api, worker, postgres, redis
- Add environment config with pydantic-settings
- Add health endpoint
- Add sample Makefile
- Add sample `.env.example`
- Implement shared domain model package with Tenant, UserPrincipal, Document, Chunk, ACL, IndexEvent
- Add minimal README with startup instructions
- Add tests for health endpoint and config loading if practical

## Definition of Done
- `docker compose up` works
- `/health` returns OK
- tests pass
- lint and typecheck pass

## Deliverables
- runnable repo scaffold
- clean local development setup
- initial domain package
- docs that explain how to boot the project

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
Initialize a monorepo for an enterprise multi-tenant RAG platform.

Create:
- apps/api (FastAPI service)
- apps/worker (background worker)
- apps/indexer placeholder if useful
- packages/core
- packages/auth
- packages/ingestion
- packages/retrieval
- packages/llm
- packages/observability
- packages/evals
- tests
- infra/compose
- infra/migrations
- docs/architecture

Set up:
- pyproject.toml
- ruff
- mypy
- pytest
- pre-commit
- Dockerfiles
- docker-compose.yml for api, worker, postgres, redis
- environment config with pydantic-settings
- health endpoint
- sample Makefile
- sample .env.example

Implement a small shared domain model package with:
- Tenant
- UserPrincipal
- Document
- Chunk
- ACL
- IndexEvent

Add a README with local startup instructions.
Run tests and ensure the repo boots successfully.

Do not implement later phases yet.
```

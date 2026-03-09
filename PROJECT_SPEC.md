# PROJECT_SPEC.md

## Project Name
Enterprise Multi-Tenant RAG Platform

## One-line Summary
Build a production-style prototype of an enterprise Retrieval-Augmented Generation platform with event-driven indexing, tenant-aware hybrid retrieval, and ACL-safe grounding for LLM answers.

## Goal
This project should demonstrate strong platform engineering skills for Staff/Principal AI Platform, Applied AI Infrastructure, and enterprise RAG system roles.

The platform must support:
- event-driven indexing
- multi-tenant isolation
- vector + lexical hybrid retrieval
- ACL-safe retrieval and grounding
- grounded answer generation with citations
- observability and evaluation
- production-minded architecture
- clean, incremental implementation

---

## Core Requirements

### Must Have
- Multi-tenant architecture
- Event-driven ingestion and indexing
- Canonical document model
- Chunking pipeline
- Vector retrieval
- Lexical retrieval
- Hybrid retrieval with score fusion
- ACL enforcement during retrieval and prompt grounding
- Grounded answer generation with citations
- Docker-based local development
- Strong automated tests
- Structured logging, metrics, traces
- Evaluation harness

### Non-Goals for v1
- No Kubernetes deployment required
- No Kafka required unless behind an interface
- No full frontend before backend is complete
- No complex distributed sharding implementation beyond a tenant-aware logical design
- No vendor lock-in in LLM or retrieval adapters

---

## Recommended Tech Stack

### Language / Runtime
- Python 3.12

### API
- FastAPI

### Data / ORM
- PostgreSQL
- SQLAlchemy
- Alembic

### Vector Index
- pgvector

### Lexical Retrieval
- PostgreSQL full-text search for v1

### Eventing
- Redis Streams for v1

### Cache
- Redis

### Storage
- Local filesystem in dev
- Storage abstraction for future S3-compatible backend

### Quality
- pytest
- mypy
- ruff
- pre-commit

### Observability
- Structured logging
- Prometheus metrics
- OpenTelemetry tracing

### Infra
- Docker
- Docker Compose

---

## High-Level Architecture

### Offline / Indexing Path
1. User or connector submits content
2. Content is normalized into a canonical document model
3. Tenant and ACL metadata are attached
4. An index event is emitted
5. A worker processes the event asynchronously
6. Content is chunked
7. Embeddings are generated
8. Lexical, vector, metadata, and chunk stores are updated
9. Index state becomes queryable

### Online / Query Path
1. User authenticates
2. Request context resolves tenant, user, groups, roles
3. Query is normalized and embedded
4. Hybrid retrieval runs:
   - lexical retrieval
   - vector retrieval
5. Results are tenant-scoped and ACL-filtered
6. Results are merged and reranked
7. Authorized chunks are passed to prompt assembly
8. LLM generates grounded answer with citations
9. System abstains if evidence is missing or insufficient

---

## Repository Structure

```text
enterprise-rag/
  apps/
    api/
    worker/
    indexer/
  packages/
    core/
    auth/
    ingestion/
    retrieval/
    llm/
    observability/
    evals/
  infra/
    compose/
    docker/
    migrations/
  docs/
    architecture/
    runbooks/
  tests/
    unit/
    integration/
    e2e/
```

---

## Engineering Standards

Codex must follow these rules throughout the project:

- Keep changes incremental and reviewable
- Do not break prior phases
- Prefer interfaces at integration boundaries
- Every feature must include tests
- Every phase must leave the repo runnable
- Update README and docs as changes land
- Keep security-sensitive code easy to audit
- Use structured logging
- Include correlation IDs
- Avoid giant files when smaller modules are clearer
- Use dependency injection where practical
- Before making changes, summarize the plan
- After changes, run:
  - `ruff check .`
  - `mypy .`
  - `pytest`
- Then summarize:
  1. what changed
  2. why
  3. risks / follow-up work

---

## Domain Model

Initial domain entities should include:
- Tenant
- User
- Group
- UserPrincipal
- Document
- DocumentVersion
- Chunk
- ACL
- ACLEntry
- IngestionJob
- IndexEvent
- Citation
- AnswerRequest
- AnswerResponse

---

## Security Model

### Tenant Isolation
Every document, chunk, event, cache entry, and retrieval result must be scoped to a `tenant_id`.

### ACL Model
Support:
- allowed users
- allowed groups
- allowed roles
- explicit deny entries
- deny precedence over allow

### Security Rule
No chunk may be:
- returned by list APIs
- returned by retrieval APIs
- passed to prompt assembly
- included in citations

unless ACL evaluation passes for the current principal.

### Enforcement Points
ACL enforcement must happen in:
- document listing
- chunk listing
- lexical retrieval
- vector retrieval
- hybrid retrieval
- final grounding selection
- cached retrieval reuse

---

## Event Model

### Event Types
- document.created
- document.updated
- document.deleted
- acl.updated
- reindex.requested

### Event Envelope
Each event should include:
- event_id
- idempotency_key
- event_type
- tenant_id
- document_id
- version_id when relevant
- occurred_at
- payload
- attempt_count
- status

### Processing Guarantees
- at-least-once delivery
- idempotent handling
- retries with exponential backoff
- dead-letter queue
- poison-message protection
- structured logs for all state transitions

---

## Caching Rules

All caches must be:
- tenant-aware
- ACL-context aware
- version-aware where relevant
- safe against cross-tenant leakage

### Cache Types
- query cache
- embedding cache
- retrieval result cache
- grounded context cache

### Cache Key Requirements
Cache keys should include:
- tenant_id
- normalized query or document hash
- ACL-related context
- model version where applicable

---

## API Scope

### Platform
- `GET /health`
- `GET /me`

### Ingestion
- `POST /v1/documents/upload`
- `POST /v1/documents/text`
- `POST /v1/documents/url`
- `GET /v1/ingestion-jobs/{job_id}`

### Documents and ACL
- `GET /v1/tenants/{tenant_id}/documents`
- `GET /v1/documents/{document_id}/chunks`
- `PATCH /v1/documents/{document_id}/acl`

### Retrieval
- `POST /v1/retrieval/search`

### Answers
- `POST /v1/answers`

### Admin / Eval
- `GET /v1/admin/metrics-summary`
- CLI command for reindex-all
- CLI command for evals

---

## Required Test Coverage

### Unit Tests
- ACL evaluator
- query normalization
- chunking logic
- embedding cache
- lexical query builder
- ranking/fusion
- prompt assembly

### Integration Tests
- upload to index pipeline
- retry and DLQ behavior
- tenant-aware retrieval
- ACL filtering
- answer generation

### End-to-End Tests
- document upload to answer flow
- cross-tenant isolation
- ACL-safe citations
- abstain behavior

---

## Observability Requirements

### Metrics
Track:
- ingestion job count
- ingestion job failures
- event lag
- event retries
- DLQ count
- chunks indexed
- embedding generation latency
- retrieval latency
- answer generation latency
- ACL rejection count

### Logging
Every request or event should include:
- correlation_id
- tenant_id
- user_id when present
- request path or event type
- status
- latency
- error details when applicable

### Tracing
Trace:
- ingestion request
- event production
- event consumption
- indexing pipeline
- retrieval path
- LLM answer path

---

## Evaluation Requirements

Build an evaluation harness that measures:
- recall@k
- mean reciprocal rank
- citation precision
- groundedness pass/fail
- abstain correctness

Dataset should include:
- exact keyword queries
- semantic queries
- ACL-restricted queries
- no-answer queries
- conflicting-evidence queries

---

## Failure Modes to Design For

Codex should explicitly consider:
- duplicate event delivery
- partial indexing failure
- stale ACL caches
- cross-tenant cache pollution
- document deletion propagation gaps
- re-embedding drift by model version
- prompt assembly using unauthorized chunks
- retrieval returning stale chunk versions
- retry storms
- poison messages
- empty evidence paths causing hallucinations

---

## Demo Tenants and Fixtures

### Tenant A: finance-co
Documents:
- audit policy
- vendor onboarding
- Q4 board memo
- incident runbook

Users:
- alice@finance-co — finance-admin
- bob@finance-co — analyst

Groups:
- finance_admins
- finance_analysts

### Tenant B: health-co
Documents:
- claims workflow
- HIPAA handling guide
- pharmacy ops memo
- escalation SOP

Users:
- cara@health-co — ops-manager
- dan@health-co — contractor

Groups:
- health_ops
- contractors

### ACL Expectations
- some docs visible to all within tenant
- some restricted to admins
- some restricted to named users
- one explicitly denied to contractors

---

## Sequence of Phases

Build in this exact order:

1. Phase 00 — Monorepo Scaffold
2. Phase 01 — Data Model + Auth Context
3. Phase 02 — Ingestion API
4. Phase 03 — Event-Driven Indexing Pipeline
5. Phase 04 — Chunking + Canonical Document Model
6. Phase 05 — Embeddings + Vector Index
7. Phase 06 — Lexical Retrieval
8. Phase 07 — Tenant-Aware Hybrid Retrieval
9. Phase 08 — ACL Enforcement in Retrieval and Grounding
10. Phase 09 — LLM Grounding + Answer Generation
11. Phase 10 — Caching, Observability, Evals
12. Phase 11 — Hardening for Demo Quality
13. Phase 12 — Scalable Adapter Interfaces

Do not skip ahead unless the earlier phase is complete and tests are green.

---

## Global Codex Working Rules

Use these in every phase:

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

After each phase, ask Codex:

```text
Review your own implementation like a senior engineer.

Provide:
- architecture review
- security review
- failure modes
- missing tests
- refactor suggestions
- next smallest safe increment

Then make only high-confidence fixes and rerun tests.
```

---

## First Task to Give Codex

Start with:
- `PROJECT_SPEC.md`
- `CODEX_TASK_00.md`

Do only Phase 00 first.

---

## Success Criteria

The project is successful when:
- documents can be ingested and indexed asynchronously
- retrieval supports lexical and vector search
- tenant isolation is enforced across all paths
- ACL filtering prevents unauthorized retrieval and grounding
- answers include citations only from authorized chunks
- the system abstains when evidence is weak or absent
- metrics, traces, and evals exist
- the repo is easy to run locally and explain in interviews

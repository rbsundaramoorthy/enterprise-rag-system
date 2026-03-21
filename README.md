# Enterprise RAG System

Phase 02 scaffold for an enterprise multi-tenant RAG platform. This repository currently provides the monorepo layout, shared domain models, the initial SQLAlchemy schema and Alembic migration path, JWT principal extraction, tenant-aware FastAPI endpoints, local raw-content ingestion flows, Redis stream event publishing, and baseline tooling.

## Layout

```text
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
  migrations/
docs/
  architecture/
tests/
```

## Local setup

1. Create a Python 3.12 environment.
2. Install dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

3. Copy `.env.example` to `.env` if you want to override defaults.
4. Run migrations and seed sample data:

```bash
make migrate
make seed
```

5. Run the API locally:

```bash
make run-api
```

6. Check health:

```bash
curl http://localhost:8000/health
```

7. Generate a dev token if you want to hit protected endpoints:

```bash
python - <<'PY'
import jwt
print(jwt.encode(
    {
        "user_id": "user-1",
        "tenant_id": "tenant-1",
        "groups": ["engineering"],
        "roles": ["member"],
    },
    "development-secret-32-bytes-minimum",
    algorithm="HS256",
))
PY
```

## Docker Compose

Start the scaffolded stack:

```bash
docker compose up --build
```

This starts:
- `api` on port `8000`
- `worker`
- `postgres`
- `redis`

Protected endpoints:
- `GET /me`
- `GET /v1/tenants/{tenant_id}/documents`
- `POST /v1/documents/upload`
- `POST /v1/documents/text`
- `POST /v1/documents/url`
- `GET /v1/ingestion-jobs/{job_id}`

Raw content is stored locally under `data/raw/{tenant_id}/{document_id}/{version}` in development. Indexing events are published to Redis Streams using `idx:events:{tenant_id}`.

## Quality checks

```bash
ruff check .
mypy .
pytest
```

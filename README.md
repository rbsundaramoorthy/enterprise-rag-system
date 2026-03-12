# Enterprise RAG System

Phase 00 scaffold for an enterprise multi-tenant RAG platform. This repository currently provides the monorepo layout, shared domain models, a minimal FastAPI service, worker and indexer placeholders, local Docker Compose infrastructure, and baseline tooling.

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
4. Run the API locally:

```bash
make run-api
```

5. Check health:

```bash
curl http://localhost:8000/health
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

## Quality checks

```bash
ruff check .
mypy .
pytest
```


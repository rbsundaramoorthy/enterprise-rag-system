FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY packages ./packages

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "enterprise_rag_worker"]


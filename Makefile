PYTHON ?= python3

.PHONY: install lint typecheck test check run-api run-worker

install:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest

check: lint typecheck test

run-api:
	uvicorn enterprise_rag_api.main:app --host 0.0.0.0 --port 8000 --reload

run-worker:
	$(PYTHON) -m enterprise_rag_worker


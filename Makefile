.PHONY: dev test lint fmt down logs ingest eval reindex

dev:
	docker compose up db api

test:
	python -m pytest tests/ -v

lint:
	ruff check . && mypy apps packages

fmt:
	ruff format .

down:
	docker compose down

logs:
	docker compose logs -f api

ingest:
	docker compose run --rm ingest

eval:
	python tests/eval/test_benchmark.py

reindex:
	@echo "Run make ingest after source changes; unchanged episodes are skipped."

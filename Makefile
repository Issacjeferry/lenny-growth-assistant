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
	python -m packages.retrieval.ingest

eval:
	@echo "Corpus benchmark is not yet implemented. See docs/assessment-review.md."
	@exit 1

reindex:
	@echo "Run make ingest after source changes; unchanged episodes are skipped."

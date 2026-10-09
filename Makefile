.PHONY: dev test lint fmt down logs ingest eval reindex

dev:
	docker compose up db api

test:
	pytest tests/ -v

lint:
	ruff check . && mypy apps packages

fmt:
	ruff format .

down:
	docker compose down

logs:
	docker compose logs -f api

ingest:
	@echo "not implemented yet"

eval:
	@echo "not implemented yet"

reindex:
	@echo "not implemented yet"

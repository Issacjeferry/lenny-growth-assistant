.PHONY: dev test lint fmt down logs ingest eval reindex setup-model

dev:
	docker compose up --build db api

test:
	python -m pytest tests/ -v
	node --test apps/agent/bridge.test.mjs
	npm --prefix apps/web test

setup-model:
	ollama pull llama3.2:3b
	ollama create lenny-local -f models/Modelfile

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
	python tests/eval/test_benchmark.py $(EVAL_ARGS)

reindex:
	@echo "Run make ingest after source changes; unchanged episodes are skipped."

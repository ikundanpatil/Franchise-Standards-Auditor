# FranchiseGuard AI backend — dev shortcuts.
.DEFAULT_GOAL := help
PY ?= python

.PHONY: help install dev run migrate makemigration seed test lint fmt docker

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime + dev dependencies
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt

run: ## Run the API with autoreload
	uvicorn app.main:app --reload --port 8000

migrate: ## Apply all migrations
	alembic upgrade head

makemigration: ## Autogenerate a migration: make makemigration m="add X"
	alembic revision --autogenerate -m "$(m)"

seed: ## Seed demo data (add FRESH=1 to drop+recreate first)
	$(PY) -m app.db.seed $(if $(FRESH),--fresh,)

test: ## Run the test suite
	$(PY) -m pytest

lint: ## Lint with ruff
	ruff check app tests

fmt: ## Format with ruff
	ruff format app tests

docker: ## Build + run the local Postgres + API stack
	docker compose up --build

# soc-worker backend — every command Naveed needs. Run `make help`.
# All targets run from backend/ through uv, so the right Python (3.12) and packages are used.

.DEFAULT_GOAL := help
SHELL := /bin/bash
UV := uv
SRC := packages/soc-shared/src scripts
TESTS := packages/soc-shared/tests tests

.PHONY: help dev test cov lint fmt typecheck check eval-dry demo-masking clean \
        eval demo-handbook demo-ask demo-triage docker-build up down

help: ## Show this list
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*## "}{printf "  %-15s %s\n", $$1, $$2}'

dev: ## Install every workspace package + dev tools (uv sync)
	$(UV) sync --all-packages

test: ## Run all tests (offline, free)
	$(UV) run pytest

cov: ## Tests with coverage (fails below 90% for soc-shared)
	$(UV) run pytest --cov --cov-report=term --cov-fail-under=90

lint: ## Ruff lint + format check
	$(UV) run ruff check .
	$(UV) run ruff format --check .

fmt: ## Auto-format and auto-fix
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

typecheck: ## mypy --strict
	$(UV) run mypy $(SRC) $(TESTS)

check: lint typecheck cov ## Every quality gate (what CI runs)

eval-dry: ## Mocked eval run (free) — added in feature 02
	@echo "eval-dry: not implemented until feature 02"

demo-masking: ## Show one lab alert before/after masking + leak check
	$(UV) run python scripts/demo_masking.py

clean: ## Remove caches and reports
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml

# ----- later features (stubs: they say which feature adds them) -----
eval: ## PAID eval run — feature 02 (needs Naveed's "haan")
	@echo "eval: added in feature 02 (paid; needs Naveed's haan)"; exit 1
demo-handbook: ## Handbook MCP smoke test — feature 04
	@echo "demo-handbook: added in feature 04"; exit 1
demo-ask: ## /ask flow in the terminal — feature 05
	@echo "demo-ask: added in feature 05"; exit 1
demo-triage: ## /triage flow in the terminal — feature 05
	@echo "demo-triage: added in feature 05"; exit 1
docker-build: ## Build all images — feature 09
	@echo "docker-build: added in feature 09"; exit 1
up: ## Start all services (compose) — feature 09
	@echo "up: added in feature 09"; exit 1
down: ## Stop all services — feature 09
	@echo "down: added in feature 09"; exit 1

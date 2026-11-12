# soc-worker backend — every command Naveed needs. Run `make help`.
# All targets run from backend/ through uv, so the right Python (3.12) and packages are used.

.DEFAULT_GOAL := help
SHELL := /bin/bash
UV := uv
SRC := packages/soc-shared/src evals/src evals/scripts scripts services/wazuh-mcp/src services/enrichment-mcp/src
TESTS := packages/soc-shared/tests evals/tests tests services/wazuh-mcp/tests services/enrichment-mcp/tests

.PHONY: help dev test cov lint fmt typecheck check eval-dry eval-stats eval-review eval-recordings \
        demo-masking clean \
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

eval-dry: ## FREE offline eval: validate datasets + score recorded predictions + write report
	$(UV) run python -m soc_evals dry

eval-stats: ## Eval dataset composition (counts, verified labels)
	$(UV) run python -m soc_evals stats

eval-review: ## Write the label review sheet for Naveed (evals/review/labels-review.md)
	$(UV) run python -m soc_evals review

eval-recordings: ## Rebuild alerts/labels/probes + dry recordings from the builder scripts
	$(UV) run python evals/scripts/build_alerts.py
	$(UV) run python evals/scripts/build_probes.py
	$(UV) run python -m soc_evals recordings

demo-masking: ## Show one lab alert before/after masking + leak check
	$(UV) run python scripts/demo_masking.py

clean: ## Remove caches and reports
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml

# ----- later features (stubs: they say which feature adds them) -----
eval: ## PAID eval run (needs Naveed's "haan"; pipeline from features 05/06)
	$(UV) run python -m soc_evals paid
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

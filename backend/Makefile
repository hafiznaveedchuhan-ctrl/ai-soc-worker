# soc-worker backend — every command Naveed needs. Run `make help`.
# All targets run from backend/ through uv, so the right Python (3.12) and packages are used.

.DEFAULT_GOAL := help
SHELL := /bin/bash
UV := uv
SRC := packages/soc-shared/src packages/ksor-client/src evals/src evals/scripts scripts services/wazuh-mcp/src services/enrichment-mcp/src services/agent-service/src services/api-gateway/src
TESTS := packages/soc-shared/tests packages/ksor-client/tests evals/tests tests services/wazuh-mcp/tests services/enrichment-mcp/tests services/agent-service/tests services/api-gateway/tests

.PHONY: help dev test cov lint fmt typecheck check eval-dry eval-stats eval-review eval-recordings \
        demo-masking demo-mcp demo-enrichment-live serve-wazuh-mcp serve-enrichment-mcp clean \
        eval demo-handbook demo-ask demo-triage docker-build up down trivy demo-up

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

demo-mcp: ## Call wazuh-mcp + enrichment-mcp in memory (free, AbuseIPDB mocked)
	$(UV) run python scripts/demo_mcp.py

demo-enrichment-live: ## ONE real AbuseIPDB call: make demo-enrichment-live IP=x.x.x.x CONFIRM=haan
	CONFIRM=$(CONFIRM) $(UV) run python scripts/demo_mcp.py --live $(IP)

serve-agent: ## Serve agent-service (internal API :8100, REAL models — paid)
	$(UV) run python -m agent_service

serve-gateway: ## Serve api-gateway (public API :8000; dev auth by default)
	$(UV) run python -m api_gateway

db-upgrade: ## Apply Alembic migrations to SOC_DB_URL from .env (Neon) — needs CONFIRM=haan
	CONFIRM=$(CONFIRM) $(UV) run python scripts/db_upgrade.py

serve-wazuh-mcp: ## Serve wazuh-mcp at http://127.0.0.1:8101/mcp (fixture mode)
	$(UV) run python -m wazuh_mcp

serve-enrichment-mcp: ## Serve enrichment-mcp at http://127.0.0.1:8102/mcp (reads ABUSEIPDB_API_KEY from env)
	$(UV) run python -m enrichment_mcp

clean: ## Remove caches and reports
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml

# ----- later features (stubs: they say which feature adds them) -----
eval: ## PAID eval run (needs Naveed's "haan"; pipeline from features 05/06)
	$(UV) run python -m soc_evals paid
demo-handbook: ## LIVE handbook search (T1: npm run serve in ../handbook): make demo-handbook Q="..." CONFIRM=haan
	CONFIRM=$(CONFIRM) $(UV) run python scripts/demo_handbook.py "$(Q)"
demo-ask: ## /ask flow (FAKE, free). LIVE: make demo-ask LIVE=1 CONFIRM=haan Q="..."
	CONFIRM=$(CONFIRM) $(UV) run python scripts/demo_agents.py ask --q "$(or $(Q),What does event 4625 mean?)" $(if $(LIVE),--live,)
demo-triage: ## /triage flow (FAKE, free, asks you to approve). LIVE: make demo-triage LIVE=1 CONFIRM=haan ID=EV-A003
	CONFIRM=$(CONFIRM) $(UV) run python scripts/demo_agents.py triage --id $(or $(ID),EV-A003) --interactive $(if $(LIVE),--live,)
GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
docker-build: ## Build the 4 images ai-soc/<svc>:<git-sha> (needs Docker)
	GIT_SHA=$(GIT_SHA) docker compose build

up: ## Start all services; gateway on http://127.0.0.1:8000 (dev auth); SQLite volume by default
	GIT_SHA=$(GIT_SHA) docker compose up -d --build && docker compose ps

down: ## Stop all services (keeps volumes; never use -v on shared stacks)
	docker compose down

trivy: ## Scan the 4 images for CRITICAL/HIGH vulnerabilities (Trivy container, free)
	for s in wazuh-mcp enrichment-mcp agent-service api-gateway; do \
	  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.67.2 image \
	    --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 ai-soc/$$s:$(GIT_SHA) || exit 1; done

demo-up: ## After `make up`: ask + triage through the running gateway (curl)
	curl -sN -X POST http://127.0.0.1:8000/ask -H "X-Dev-User: naveed:analyst" -H "Content-Type: application/json" -d '{"question":"What does event 4625 mean?"}'; echo
	curl -s -X POST http://127.0.0.1:8000/triage/EV-A003 -H "X-Dev-User: naveed:analyst" -H "Content-Type: application/json" -d '{}'; echo

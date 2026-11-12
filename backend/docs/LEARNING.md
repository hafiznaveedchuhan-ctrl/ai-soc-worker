# LEARNING.md — soc-worker, explained file by file

Written for Naveed, in simple English. Each feature adds its own section. Read one section,
then open the files it names and run the command it shows.

Contents: [1 Big picture](#1-big-picture) · [2 Feature 01 — foundation](#2-feature-01--foundation) ·
[3 Masking](#3-how-masking-works) · [4 Data contracts](#4-the-data-contracts-models) ·
[5 Tests](#5-how-the-tests-work) · [6 CI pipeline](#6-ci-pipeline-githubworkflowsciyml) ·
[7 Later features](#7-later-features-placeholders) · [8 Evals](#8-feature-02--evals-first) · [9 MCP services](#9-feature-03--mcp-services) · [10 Handbook client](#10-feature-04--handbook-client) · [11 Agents + guardrails](#11-features-05-06--agents-and-guardrails) · [12 Gateway + Docker](#12-features-07-09--internal-api-gateway-docker) · [13 CI/CD](#13-feature-10--cicd)

---

## 1. Big picture
soc-worker is an **AI SOC Triage Copilot**. It reads Wazuh alerts and analyst questions, checks the
governed handbook (KSOR, over MCP), and writes **cited suggestions**. A human analyst always decides.
Four services will run it (api-gateway, agent-service, wazuh-mcp, enrichment-mcp) plus one shared
library (soc-shared). Diagrams: `architecture.md`. Plan: `../../specs/00-final-plan.txt`.

How the work is organised (Spec-Driven Development):
`specs/NN-name/INTENT.md` (why) → `spec.md` (what) → `plan.md` (how) → `tasks.md` (steps) →
code → `VERIFY.md` (proof). Big decisions → `docs/adr/`. Every important prompt → `history/prompts/` (PHR).
`progress.md` at the repo root tells any new session where we are.

---

## 2. Feature 01 — foundation

### Folder map
| Path | What it is | Why | Command that uses it |
|---|---|---|---|
| `CLAUDE.md` (repo root) | Rules for the AI assistant: session protocol, hard rules, SDD steps | The same rules every session | read at session start |
| `progress.md` (root) | Append-only session log + "READ ME FIRST" box | A new session knows exactly where we are | read at session start |
| `specs/constitution.md` | The 10 articles that win over everything | Safety, privacy, cost, quality rules in one place | — |
| `specs/_templates/` | INTENT/spec/plan/tasks/VERIFY templates | Every feature has the same shape | copied per feature |
| `backend/pyproject.toml` | **Workspace root**: lists members, dev tools, ruff/mypy/pytest config | One lockfile and one tool config for all services (ADR-0001) | `uv sync`, all `make` targets |
| `backend/.python-version` | `3.12` | Without it uv picked Python 3.13 | uv reads it |
| `backend/uv.lock` | Exact versions of every package | Same versions on your laptop and in CI | `uv sync --frozen` |
| `backend/Makefile` | Short names for long commands | `make test` instead of `uv run pytest ...` | `make help` |
| `backend/.env.example` | Names of the environment variables (no values) | Shows what to put in your own `.env` | you copy it to `.env` |
| `backend/packages/soc-shared/` | The shared library | Models + masking used by every service | imported as `soc_shared` |
| `backend/scripts/demo_masking.py` | The feature 01 demo | See masking work with your own eyes | `make demo-masking` |
| `backend/tests/test_repo_hygiene.py` | Checks `.env.example` and `.gitignore` | A secret can never slip into the repo by mistake | `make test` |
| `backend/services/`, `evals/`, `suggestions/` | Empty for now (`.gitkeep`) | Filled by features 02, 03, 05–08 | — |
| `backend/docs/adr/` | Architecture Decision Records | Why we chose X over Y | — |
| `.github/workflows/ci.yml` | The CI pipeline | Every push is checked automatically | runs on GitHub |
| `.gitleaks.toml` | Secret-scanner config | Finds keys/passwords in any commit | CI `secrets` job |

### uv workspace explained
- A **workspace** is one folder (`backend/`) holding several Python projects that share **one lockfile**.
- `backend/pyproject.toml` has no `[project]` table — it is a *virtual root*: it only says which folders
  are members (`[tool.uv.workspace] members = ["packages/*"]`) and which dev tools everyone uses
  (`[dependency-groups] dev = [...]`).
- `soc-shared = { workspace = true }` under `[tool.uv.sources]` means: "take soc-shared from this repo,
  not from PyPI" (installed in *editable* mode, so code changes are seen immediately).
- Services will be added as members one by one (uv needs a `pyproject.toml` in every member folder).
- Commands: `uv sync --all-packages` (install everything) · `uv run <cmd>` (run inside the workspace venv) ·
  `uv add <pkg>` (inside a member folder: add a runtime dependency) · `uv add --dev <pkg>` (in `backend/`: add a dev tool).

### The `src/` layout
`packages/soc-shared/src/soc_shared/...` — code lives under `src/` so tests import the **installed**
package, not a random folder. `py.typed` tells mypy "this package ships type hints".

### Makefile basics
A target is `name: ## help text` followed by indented commands (a **tab**, not spaces).
`make help` greps the `## ` comments. `.PHONY` says the targets are commands, not files.
Targets of later features exist as **stubs** that say which feature adds them and exit with an error.

---

## 3. How masking works
**Why:** the handbook's invariant 4 and data-handling page — IPs, usernames, hostnames (and our emails)
are replaced by tokens **before** any LLM, web call, log line or trace. The model only sees `<IP-1>`, `<USER-1>`…

| File | Job |
|---|---|
| `masking/ipclass.py` | Is this IP public, private (which RFC 1918 range), or special (loopback, documentation…)? Uses Python's `ipaddress` parser + explicit lists. Only `public` may go to AbuseIPDB. |
| `masking/maskmap.py` | `MaskMap`: the table value ⇄ token for ONE request. Same value → same token (`Admin` = `admin`, `2001:DB8::1` = `2001:db8::1`). `repr()` shows counts only. |
| `masking/patterns.py` | The regexes (email, `DOMAIN\user`, IPv4, IPv6, internal FQDN), built-in principals, secret field names. |
| `masking/text.py` | `mask_text` (free text), `unmask` (gateway only), `find_leaks`, `find_unmasked_pii` (checks used by tests and later by the output guardrail). |
| `masking/alert.py` | `mask_alert`: masks a whole Wazuh alert. |

**`mask_alert` in two passes**
1. **Field-aware pass** — we know what some fields mean: `agent.name`, `data.win.system.computer` → HOST;
   `data.srcip`, `ipAddress` → IP; `targetUserName`, `dstuser` → USER. A `$` at the end (`LAB-WS01$`) means a
   *computer account* → HOST. Fields named like secrets (`password`…) are **dropped** and listed in `dropped_fields`.
2. **Free-text pass** — `mask_text` runs over every other string (e.g. `full_log`), so a name learned in
   pass 1 (`alice`) is masked inside sentences too.

**`mask_text` order:** emails → `DOMAIN\user` → IPv6 → IPv4 → internal FQDNs (`.local .lan .corp .internal .intra .home.arpa`)
→ learned host/user names. IPv6 comes first so `::ffff:10.0.0.5` becomes the same token as `10.0.0.5`.
Regexes only *find candidates*; `ipaddress` decides, so `12:30:45`, MAC addresses and `10.0.19041.1` are not masked.

**What is deliberately NOT masked (and why)**
- Built-in principals: `SYSTEM`, `LOCAL SERVICE`, `NETWORK SERVICE`, `ANONYMOUS LOGON`, `Administrator`, `Guest`,
  `DefaultAccount`, `krbtgt`, `root` — not personal data, and escalation condition 2 needs to see "privileged account".
- File hashes (Sysmon `hashes`) — they are IOCs the analyst needs (your decision Q1).
- Public domains (`attack.mitre.org`) and URLs' paths — they are evidence, not personal data.
- Alert id, rule id/level/description, timestamps, Event IDs, logon types, status codes.
- `ip_context` tells the model the *range* of a private IP (`private 10.0.0.0/8`) but never the value (your decision Q2).

**Known limits (tested, documented):** a short hostname that appears only in free text (never in a field)
and has no internal suffix is not detected; learned names shorter than 3 characters are only masked in their own field.
Feature 06's output guardrail runs `find_leaks` as a second safety net.

---

## 4. The data contracts (models)
All in `packages/soc-shared/src/soc_shared/models/`, Pydantic v2.

| Model | File | Key rules |
|---|---|---|
| `WazuhAlert` | `alert.py` | rule level 0–15; extra Wazuh fields allowed; `+0000` time offsets fixed |
| `MaskedAlert` | `alert.py` | the ONLY alert form that may reach an LLM |
| `KsorHit` | `ksor.py` | `stable_id` must look like `knowledge/...`; `gate` defaults to `"off"` |
| `ScopeVerdict`, `DECLINE_MESSAGE` | `scope.py` | 3 labels (ADR-0002); the exact decline sentence |
| `TriageNote` | `note.py` | handbook template; escalate ⇔ condition 1–8; needs_info ⇒ missing_info; a verdict needs a KSOR citation (a web source alone is never enough); `final_decision_by` is always `"human"`; `to_text()` prints the template |
| `AskAnswer` | `answer.py` | cite, or label a web source, or say not_in_record; a DECLINE answer must be the exact sentence |
| `Decision`, `AuditEvent`, `LlmUsage` | `audit.py` | human decision approve/change/escalate; usage tokens ≥ 0 |

Pydantic ideas used: `ConfigDict(extra="forbid")` (typos become errors) · `frozen=True` (value objects) ·
`Field(ge=, le=, pattern=)` (constraints) · `@model_validator(mode="after")` (rules across fields) ·
`StrEnum` (enum values serialise as plain strings in JSON).

---

## 5. How the tests work
- `make test` runs **153 tests in about 15 seconds, fully offline**: `--disable-socket` (pytest-socket) makes any
  network attempt fail the test.
- **Unit tests** — one behaviour each (`test_models.py`, `test_triage_note.py`, `test_ipclass.py`, `test_masking.py`).
- **Golden tests** — the exact expected output (`test_to_text_golden`, `test_mask_alert.py`).
- **Property tests** (`test_masking_properties.py`, Hypothesis) — the computer invents 600 random texts with
  random IPv4/IPv6/emails and checks: nothing leaks · `unmask(mask(x)) == x` · masking twice changes nothing.
- **Performance budget** (`test_masking_perf.py`) — a 50 KB alert masks in about 20–30 ms.
- **Coverage** (`make cov`) — at least 90% of soc-shared lines must run in tests (it is 99%).
- Fixtures (`tests/fixtures/*.json`) use only documentation IPs (RFC 5737), RFC 1918 and invented names.

---

## 6. CI pipeline (`.github/workflows/ci.yml`)
| Line / step | What it does | Why |
|---|---|---|
| `on: pull_request` + `push: feat/**` | Runs on every PR and every push to a feature branch | Problems are found before merge |
| `permissions: contents: read` | The job token can only read | Least privilege |
| `concurrency … cancel-in-progress` | A new push cancels the older run | Saves free CI minutes |
| `actions/checkout@<sha>` | Downloads the repo | Pinned by commit SHA: a moved tag cannot inject code |
| `astral-sh/setup-uv@<sha>` + cache | Installs uv; caches downloads | Fast, same tool as your laptop |
| `uv sync --all-packages --frozen` | Installs exactly `uv.lock` | Fails if the lock is out of date |
| ruff check / ruff format --check | Lint + formatting | Clean, consistent code |
| mypy | Type check (strict) | Catches wrong types before runtime |
| pytest --cov --cov-fail-under=90 | Tests + coverage gate | Red if coverage drops |
| masking demo | Must print `LEAK CHECK: OK` | The demo you run is also proven in CI |
| `secrets` job, `fetch-depth: 0` | Full git history | A key in an old commit is still a leak |
| gitleaks binary v8.30.1 | Scans every commit for secrets (`--redact` hides them in the log) | Free, no licence key needed |

Feature 10 adds: path filters (only changed services run), eval-dry gate, Docker build, Trivy scan, release to GHCR.

---

## 7. Later features (placeholders)
03 MCP services · 04 handbook client · 05 agents core · 06 guardrails · 07 agent-service ·
08 api-gateway · 09 Docker (every Dockerfile line explained) · 10 CI/CD.

---

## 8. Feature 02 — evals-first

**Why evals come first:** before an agent exists we decide what "good" means, with numbers. Later every prompt change,
model change or guardrail change is judged by the same tests, not by a feeling.

### Folder map (`backend/evals/`)
| Path | What | Command |
|---|---|---|
| `data/alerts/EV-A001…A040.json` | 40 Wazuh-shaped alerts: 34 SYNTHETIC (lab values) + 6 mapped from OTRF Security-Datasets | built by `scripts/build_alerts.py` |
| `data/labels.csv` | the expected answer per alert: verdict, severity, escalate + condition (+ `also_conditions`), MITRE, handbook pages, rule source, rationale, `verified_by` | `make eval-review` to read it |
| `data/context.csv` | analyst-provided context (change tickets, CDB-list membership, related alerts) — an INPUT, masked like the alert | — |
| `data/scope/probes.csv` | 95 scope questions in 4 sets (DECLINE 30, ALLOW_CYBER_RESEARCH 25, ALLOW_KSOR 30, NON_CYBER 10) | `scripts/build_probes.py` |
| `data/reference/ksor_*.txt` | read-only snapshot of the handbook's page ids and MITRE page ids | `scripts/snapshot_ksor_refs.py` |
| `data/THIRD_PARTY_NOTICES.md` | OTRF MIT licence + which Wazuh rule lines were read | — |
| `recordings/dry/oracle-*.jsonl` | "perfect" predictions made from the labels | `make eval-recordings` |
| `recordings/dry/faulty-*.jsonl` | the oracle + 7 planted mistakes | same |
| `reports/template.md` | the report layout | `make eval-dry` writes `reports/<date>-dry-report.md` |
| `review/labels-review.md` | the sheet Naveed uses to verify labels (values masked as the AI sees them) | `make eval-review` |
| `src/soc_evals/` | loader, `Rate`, scorers (triage, scope, cost), targets, report, CLI | `uv run python -m soc_evals …` |

### Key ideas
- **Labels live outside the alert JSON.** `WazuhAlert` accepts extra fields, so a `_meta.verdict` inside an alert would ride
  into the prompt and leak the answer. A test checks no alert file contains label words.
- **Every fact traces to a source.** Rule id/level/MITRE come from a handbook page or a recorded Wazuh ruleset line; a test fails
  on any other MITRE id. The scorer's "invented MITRE" check even caught one of Claude's own label mistakes (EV-A036).
- **Count + percent + set size:** `Rate(19, 21)` prints `19/21 = 90.5%`. A bare "90%" hides that one alert moves it ~5 points.
- **Precision vs recall in SOC words:** recall = "of the real attacks, how many did the AI call TP?" (a miss is dangerous);
  precision = "of the alerts the AI called TP, how many were real?" (a false alarm wastes analyst time). Target: recall ≥ 95%, precision ≥ 80%.
- **Confusion matrix:** rows = the label, columns = the AI's verdict; the diagonal is correct.
- **Testing the tester:** the oracle recording must PASS every target (else the scorer or data is wrong); the faulty recording
  must fail exactly the planted checks (else a check is blind).
- **p95 latency (nearest rank):** sort the latencies; take the value at position ⌈0.95·n⌉. 95% of requests were at least that fast.
- **Severity is not a guess:** the handbook severity model maps rule level + escalation condition to Low/Medium/High/Critical; the builder computes it.
- **Detection gap (real lesson):** 4 public attack recordings (CMSTP UAC bypass, bitsadmin download, two LSASS dumps with access
  mask 0x1FFFFF) raise **no** alert in the default Wazuh v4.14.10 ruleset — rule 92900 only checks masks 0x1010/0x40. A SOC must know what its SIEM does not see.

### Commands
`make eval-dry` (free, offline, in CI) · `make eval-stats` · `make eval-review` · `make eval-recordings` (rebuild data + recordings) ·
`make eval` (PAID — refuses until features 05/06 and Naveed's "haan").

---

## 9. Feature 03 — MCP services

**MCP (Model Context Protocol)** is a standard way for an AI app to call *tools* on a *server*. A server lists its tools
(name, input schema from type hints, annotations such as `read_only_hint`) and answers `call_tool`. We use the official
MCP Python SDK **v2.3.0** (`MCPServer`, formerly `FastMCP`), which resolves together with the OpenAI Agents SDK.

| File | What it does |
|---|---|
| `services/wazuh-mcp/src/wazuh_mcp/server.py` | `build_server(source)` registers `get_alert` and `get_new_alerts`; input checks raise `ToolError` (the model sees a clear error, the server never crashes) |
| `.../wazuh_mcp/sources.py` | `FixtureSource` reads the 40 eval alerts once; `LiveSource` is a placeholder for the read-only indexer user |
| `.../wazuh_mcp/__main__.py` | `python -m wazuh_mcp` → streamable HTTP on :8101 |
| `services/enrichment-mcp/src/enrichment_mcp/server.py` | `ip_reputation`: classify the IP → `not_queried` unless public → cache → key/budget checks → AbuseIPDB → validated result |
| `.../enrichment_mcp/abuseipdb.py` | the HTTP client + a Pydantic model of the response; every HTTP problem becomes an `AbuseIpdbError(reason)` |
| `.../enrichment_mcp/cache.py` | `TtlCache[T]` and `DailyBudget` with an injectable clock (so tests can move time) |
| `.../enrichment_mcp/bands.py` | the handbook score bands |
| `scripts/demo_mcp.py` | `make demo-mcp` — both servers in memory, AbuseIPDB mocked |

**How the tests stay free and offline:** `Client(server)` connects to the server object *in memory* (no port, no process),
and `httpx.MockTransport` answers the AbuseIPDB calls. pytest-socket blocks internet sockets; `--allow-unix-socket` is needed only
for asyncio's internal self-pipe.

**Why "errors as results":** the agent must be able to say "reputation unavailable (rate limited)" in a note, not crash the triage.

**A privacy bug found by the demo:** httpx logs every request URL at INFO, and the AbuseIPDB URL contains `?ipAddress=<IP>`.
The server now sets the httpx/httpcore loggers to WARNING, and a test captures ALL loggers to prove no IP is written.

**Read-only by design:** annotations say `read_only_hint=True`; more importantly, no write tool exists, and a test fails if one is added.

---

## 10. Feature 04 — handbook client

`backend/packages/ksor-client` talks to the handbook's KSOR MCP server (`npm run serve` in ../handbook → `127.0.0.1:8080/mcp`).

| File | What |
|---|---|
| `models.py` | Pydantic copies of the KSOR wire shapes (`SEARCH_OUTPUT`, `READ_OUTPUT`, `OUTLINE_OUTPUT`) read from the installed `@panaversity/ksor` package; `extra="ignore"` so new server fields never break us |
| `client.py` | `KsorClient.search/read/outline`, `SearchOutcome`, `not_in_record()`, `search_once()` |
| `testing.py` | `build_fake_ksor(mode)` — an in-memory MCP server with the same tools and shapes, so tests (and feature 05) run offline |
| `../../scripts/demo_handbook.py` | `make demo-handbook Q="..." CONFIRM=haan` — the live 2-terminal smoke test |

**Three kinds of "no answer" — never mix them up:**
- `abstained` → the record says it does not cover this → the agent may say **"not in this record"**.
- `unavailable` (retrieval failed, server down, embeddings down) → say "the handbook is unavailable"; it is NOT absence.
- `unpublished` (nothing ingested) → the same: no claim about coverage.

The handbook's gate is OFF (decision C), so in practice `search` almost never abstains. That is why our Scope Guard
(feature 06) must decline out-of-scope questions BEFORE any search.

**`stable_id`** (`provenance.stable_id`, e.g. `knowledge/windows-events/event-4625`) is what every citation uses.
**Snippets are capped** (1,200 characters) because passages are untrusted text that will go into prompts.
**Why a live search needs "haan":** the handbook server embeds every query with OpenAI (a tiny cost on the handbook's key).

---

## 11. Features 05-06 — agents and guardrails

### The agents (`services/agent-service/src/agent_service/agents_build.py`)
| Agent | Role | Model |
|---|---|---|
| `triage_agent` | /ask router: its instructions are a *function* that reads the Scope Guard verdict and hands off | gpt-5-nano |
| `soc_handbook_agent` | answers from KSOR via `search_handbook`, cites stable_ids, `output_type=AskAnswer` | gpt-5-nano |
| `cyber_research_agent` | defensive topics not in KSOR via `web_search` (trusted domains), saves draft suggestions | gpt-5-nano |
| `triage_coordinator` | /triage: calls the two agents **as tools** (it keeps control) + get_alert, ip_reputation, the MOCK ticket; `output_type=TriageNote` | gpt-5-nano |
| `scope_classifier` | tiny agent INSIDE the input guardrail, `output_type=ScopeVerdict` | gpt-5-nano |
| `note_reviewer` | tiny agent INSIDE the output guardrail (reflection) | gpt-5-nano |

### Handoff vs agent-as-tool
- **handoff** (/ask): the conversation moves to the specialist; the specialist's answer IS the final answer.
- **as_tool** (/triage): the coordinator calls a specialist like a function, reads its answer, and continues; it writes the final TriageNote.

### Request flow /ask, step by step
1. `run_ask` masks the question in code (`<IP-1>` …) and builds a `WorkerContext` (budget, mask map, request id).
2. `Runner.run(triage_agent, …, session=SQLiteSession, hooks=CostHooks, run_config=RunConfig(trace_include_sensitive_data=False))`.
3. **Scope Guard** runs first and BLOCKS (`run_in_parallel=False`): regex pre-check, else the classifier agent. DECLINE → tripwire → the exact
   decline sentence; no other model or tool ran.
4. `triage_agent` hands off to the handbook or research agent; that agent calls its tool(s) (tool guardrails check the inputs/outputs).
5. **Note Reviewer** (output guardrail) checks leaks, action claims, citations against what KSOR/web really returned, then the LLM reviewer.
6. The result (answer, usage with cost, mask entries, events, trace id) goes back to the caller.

### Request flow /triage, step by step
1. Code fetches the alert (wazuh-mcp), masks it, records rule level and MITRE ids in the context.
2. The coordinator asks the handbook agent (as a tool), checks public-IP reputation (`ip_reputation(<IP-n>)` — the token is unmasked
   only inside the tool code; documentation/private IPs are refused with a correction), and may propose the MOCK escalation ticket.
3. `needs_approval=True` pauses the run → `result.interruptions` → the human says y/N → `state.approve()` / `state.reject()` → the run resumes.
4. The TriageNote passes the reviewer (e.g. rule level ≥ 12 must escalate; MITRE ids must come from the alert or cited MITRE pages).

### Testing without paying: `agents.testing.ScriptedModel`
Each agent gets its own scripted model: a list of steps such as `function_call("search_handbook", {...})` then `assistant_message(json)`.
`model.calls` lets a test inspect exactly what the model was sent (e.g. "no raw IP in any input").

### Cost control
`CostHooks.on_llm_end` prices every call (input/output tokens × the price table) into `RunBudget`; over the per-run limit → `BudgetExceeded`
stops the run. The ledger file keeps the cumulative total and refuses new runs at $9. Guardrail-internal runs are priced too (a bug the
tests caught: they were first uncounted).

### The four guardrail kinds (`guardrails.py`)
input (scope) · output (reviewer) · tool input (query / IP token / web query) · tool output (web content / reputation schema). Hosted tools and
`as_tool` skip tool guardrails, so every external call is our own `@function_tool`.

---

## 12. Features 07-09 — internal API, gateway, Docker

**agent-service API (07):** internal FastAPI; `X-Internal-Token` checked with `hmac.compare_digest` (constant time); SSE via
`fastapi.sse.EventSourceResponse` (events `delta`, `final`, `done`). **api-gateway (08):** the only public service and the only DB user;
`/ask` streams `status → final → done`; stored text is masked, responses are unmasked for the analyst; `mask_map` values are Fernet-encrypted.
Two real bugs the tests found: an HTTPException raised inside an SSE generator never becomes an HTTP status (checks moved to a dependency that
runs before the stream), and Alembic's `fileConfig()` disables every existing logger unless `disable_existing_loggers=False`.

### Dockerfile, line by line (`services/<svc>/Dockerfile`, build context = `backend/`)
| Line | Why |
|---|---|
| `# syntax=docker/dockerfile:1` | enables BuildKit features such as `--mount=type=cache` |
| `FROM ghcr.io/astral-sh/uv:0.12.6-python3.12-trixie-slim AS builder` | stage 1 = an image that already has uv + Python 3.12 (exact version pinned; the bookworm tag does not exist for 0.12.6, so trixie = Debian 13) |
| `ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0` | precompile .pyc (faster start), copy files instead of hard links (works across layers), use the image's Python |
| `WORKDIR /app` · `COPY . .` | the whole workspace is copied so uv can read every member's pyproject; `.dockerignore` removes `.env`, tests, caches, docs |
| `RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable --package <svc>` | install exactly `uv.lock`, without dev tools, as real (non-editable) packages, only what this service needs; the cache mount makes rebuilds fast and is not stored in the image |
| `FROM python:3.12-slim-trixie AS runtime` | stage 2 = a small image without uv or build tools; same Python path as the builder, so the venv works |
| `RUN groupadd … useradd … --uid 10001 … mkdir -p /data` | a non-root user; `/data` for volumes (ledger, sessions, SQLite) |
| `COPY --from=builder --chown=app:app /app/.venv /app/.venv` | only the finished venv crosses over — source trees and caches stay behind |
| wazuh-mcp: `COPY evals/data/alerts /app/fixtures` | the 40 lab alerts it serves in fixture mode |
| `ENV PATH=/app/.venv/bin:$PATH PYTHONUNBUFFERED=1 …` + per-service `ENV` | the venv first; logs appear at once; bind 0.0.0.0 inside the container; data paths under `/data` |
| `USER app` | everything below runs without root |
| `EXPOSE <port>` | documentation of the port (8101, 8102, 8100, 8000) |
| `HEALTHCHECK … CMD python -c …` | Docker marks the container unhealthy if `/health` (HTTP services) or the TCP port (MCP servers) stops answering |
| `CMD ["python", "-m", "<package>"]` | exec form: the Python process is PID 1 and receives stop signals |

### compose.yaml
One network `soc`; **only the gateway publishes a port**, bound to `127.0.0.1:8000`. Every container is `read_only` with a `tmpfs` /tmp and
`no-new-privileges`. Each service gets ONLY its own variables (the AbuseIPDB key only reaches enrichment-mcp; the DB URL and the mask-map key only
the gateway). The MCP servers set `MCP_ALLOWED_HOSTS` because mcp 2.3.0 enables DNS-rebinding protection automatically only on 127.0.0.1.
The handbook runs on the host: containers use `host.docker.internal` (`extra_hosts: host-gateway`); the handbook must listen on an address the Docker
host can reach (its default 127.0.0.1 inside WSL is not reachable from Docker Desktop containers — set `HANDBOOK_MCP_URL_DOCKER` accordingly).
Commands: `make docker-build` · `make up` · `make demo-up` · `make down` · `make trivy`. Images: `ai-soc/<svc>:<git-sha>`.

---

## 13. Feature 10 — CI/CD

### `ci.yml` (every PR + every push to `feat/**`)
| Job / step | What | Why |
|---|---|---|
| `changes` + `dorny/paths-filter` | lists which services changed (a change under `packages/` or `uv.lock` counts for all) | only changed images are built — saves minutes |
| `python` · setup-uv · `uv sync --frozen` | the exact locked environment | same versions as on your laptop |
| ruff check / format --check · `make typecheck` | style and types | catch mistakes before review |
| pytest + coverage ≥ 90% | ~300 offline tests (no LLM, no network) | the main quality gate |
| masking demo · MCP demo · agent demos (fake) | the demos you run are also proven in CI | demos never rot |
| `make eval-dry` | datasets valid + scorer correct | the evals-first gate |
| `secrets` · gitleaks over full history | no key in any commit | a leaked key is permanent |
| `images` (matrix of changed services) · buildx · build-push-action `load: true` | builds `ai-soc/<svc>:<sha>`, not pushed | proves every Dockerfile builds |
| Trivy (`severity: CRITICAL`, `ignore-unfixed`) | scans the built image | blocks images with fixable critical CVEs |
All actions are pinned by commit SHA (a moved tag cannot inject code); `permissions: contents: read` (least privilege).

### `release.yml` — manual (`workflow_dispatch`) and only with input `confirm=haan` on `main`
Logs in to ghcr.io with the built-in `GITHUB_TOKEN` (`packages: write`), pushes `ghcr.io/<owner>/ai-soc-<svc>:<sha>`. The first push is your decision.

### `deploy.yml` — Phase 8 placeholder (`if: false`)
Azure Container Registry + Container Apps with OIDC; needs paid-service decisions, Postgres sessions and real Auth0 first.

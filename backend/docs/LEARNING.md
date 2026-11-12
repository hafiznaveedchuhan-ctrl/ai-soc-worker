# LEARNING.md — soc-worker, explained file by file

Written for Naveed, in simple English. Each feature adds its own section. Read one section,
then open the files it names and run the command it shows.

Contents: [1 Big picture](#1-big-picture) · [2 Feature 01 — foundation](#2-feature-01--foundation) ·
[3 Masking](#3-how-masking-works) · [4 Data contracts](#4-the-data-contracts-models) ·
[5 Tests](#5-how-the-tests-work) · [6 CI pipeline](#6-ci-pipeline-githubworkflowsciyml) ·
[7 Later features](#7-later-features-placeholders)

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
02 evals-first · 03 MCP services · 04 handbook client · 05 agents core · 06 guardrails · 07 agent-service ·
08 api-gateway · 09 Docker (every Dockerfile line explained) · 10 CI/CD.

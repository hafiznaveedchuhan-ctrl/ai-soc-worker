# spec — 01 foundation
Status: **approved** (human:naveed, 2026-11-12) · Intent: `./INTENT.md` · Plan of record: `../00-final-plan.txt` §11
Sources (read only): `../handbook/knowledge/rules-map/data-handling.md`, `.../invariants.md`, `.../escalation-policy.md`,
`../handbook/knowledge/triage-note/note-template.md`.

## 1. Summary
Feature 01 delivers (a) the uv workspace, (b) package `soc-shared` = models + masking + settings, (c) the developer
tooling (Makefile, `.env.example`, CI skeleton, gitleaks config), (d) the learning docs, (e) removal of the root scaffold.

## 2. Functional requirements

### 2.1 Workspace and tooling
| ID | Requirement | Acceptance |
|---|---|---|
| FR-01-01 | `backend/pyproject.toml` is a uv workspace root with members `packages/*` and `services/*` (services are empty until 03). | `cd backend && uv sync` succeeds; `uv.lock` is created and committed. |
| FR-01-02 | `packages/soc-shared` is an installable package `soc_shared` (src layout, `py.typed`). | `uv run python -c "import soc_shared"` works. |
| FR-01-03 | The root scaffold (`/pyproject.toml`, `/src/soc_worker/`) is removed. | `git status` shows them deleted; nothing imports `soc_worker`. |
| FR-01-04 | `backend/Makefile` has the targets `help dev test cov lint fmt typecheck eval-dry demo-masking clean`; `eval-dry` prints "not implemented until feature 02" and exits 0. Targets of later features (`eval`, `docker-build`, `up`, `down`, `demo-*`) exist as stubs that say which feature adds them and exit 1. | `make help` lists every target with one line each. |
| FR-01-05 | `backend/.env.example` lists variable NAMES only, grouped per service, each with a one-line comment. The only value present: `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=0`. | Test `test_env_example.py`: every non-comment line matches `^[A-Z][A-Z0-9_]*=$`, except that one line. |
| FR-01-06 | `.github/workflows/ci.yml` runs on pull_request and on pushes to `feat/**`: job `python` (setup-uv, `uv sync --frozen`, ruff check, ruff format --check, mypy, pytest with coverage) and job `secrets` (gitleaks over the full history). | The workflow is valid YAML; it runs green on the PR (S7). |
| FR-01-07 | Root `.gitignore` also ignores `backend/.env`, `**/.env`, `.coverage`, `htmlcov/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `*.sqlite`; it keeps `.env.example`. | `git check-ignore backend/.env` matches; `git check-ignore backend/.env.example` does not. |
| FR-01-08 | `.gitleaks.toml` extends the default rules and allow-lists documentation IP ranges and `<IP-n>`-style tokens only. | `gitleaks detect` exits 0 on the repo. |

### 2.2 Data contracts (`soc_shared.models`) — Pydantic v2
| ID | Requirement | Acceptance |
|---|---|---|
| FR-01-10 | `WazuhAlert`: `id: str`, `timestamp: datetime`, `rule: WazuhRule(id: str, level: int 0–15, description: str, groups: list[str], mitre: WazuhMitre(id/tactic/technique: list[str]) = empty)`, `agent: WazuhAgent(id: str, name: str, ip: str | None)`, `location: str | None`, `decoder: dict | None`, `data: dict[str, Any] = {}`, `full_log: str | None`. `extra="allow"` (Wazuh adds fields). | It parses a sample Wazuh 4.x alert JSON fixture; `level=16` → ValidationError. |
| FR-01-11 | `MaskedAlert`: `alert_id: str`, `rule_id: str`, `rule_level: int`, `payload: dict[str, Any]` (the masked alert), `ip_context: dict[str, str]` (token → "public" or "private <CIDR>" or "special <kind>"), `dropped_fields: list[str]`. | Built only by `Masker.mask_alert`; it never holds a raw value (property test). |
| FR-01-12 | Fields named like secrets (`*pass*`/`password`/`passwd`, `pwd`, `*secret*`, `api_key`/`apikey`, `*access/auth/refresh/bearer_token`, `*ntlm_hash`/`*lm_hash`; Windows fields like `tokenElevationType` and file `hashes` are NOT secrets) are DROPPED by `mask_alert` and listed in `dropped_fields`. | Test with `data.win.eventdata.password` → dropped. |
| FR-01-13 | `KsorHit`: `stable_id` (regex `^knowledge/[a-z0-9][a-z0-9/_-]*$`), `title: str`, `snippet: str`, `score: float | None`, `gate: Literal["off","on"]`, `heading: str | None`. | Invalid stable_id → ValidationError. |
| FR-01-14 | `Evidence(fact: str, source: str)`, `WebSource(url: HttpUrl, title: str | None, label: Literal["unverified"]="unverified")`, `IpReputation(token: str, is_public: bool, abuse_confidence_score: int 0–100 | None, total_reports: int | None, country_code: str | None, checked_at: datetime | None)`. | Unit tests per model. |
| FR-01-15 | `TriageNote` follows the handbook note template: `alert_id`, `rule_id`, `rule_level`, `time_window_start/end: datetime`, `summary`, `evidence: list[Evidence]` (≥ 1), `inference: list[str]`, `mitre_ids: list[str]` (each `^T\d{4}(\.\d{3})?$`), `citations: list[str]` (stable_ids), `web_sources: list[WebSource]`, `ip_reputation: list[IpReputation]`, `verdict_suggestion: Verdict` (`TP`, `benign_TP`, `FP`, `needs_info`), `confidence: float 0–1`, `severity: Severity` (`Low`,`Medium`,`High`,`Critical`), `escalate: bool`, `escalate_condition: int 1–8 | None`, `escalate_reason: str | None`, `missing_info: list[str]`, `final_decision_by: Literal["human"]="human"`. | See FR-01-16 validators. |
| FR-01-16 | `TriageNote` validators: (a) `escalate=True` ⇔ `escalate_condition` set; (b) `verdict=needs_info` ⇒ `missing_info` non-empty; (c) `verdict ∈ {TP, benign_TP, FP}` or `escalate=True` ⇒ at least one KSOR citation (a web source alone is never enough — constitution IV.3); (d) `confidence_band` property → `low` (<0.40) / `medium` (<0.70) / `high`; (e) `to_text()` renders the handbook template in its exact field order, last line exactly `Final decision: human analyst`. | One test per validator; a golden-text test for `to_text()`. |
| FR-01-17 | `AskAnswer`: `answer: str`, `scope: ScopeLabel`, `citations: list[str]`, `web_sources: list[WebSource]`, `not_in_record: bool`, `confidence: float 0–1`. Validator: a non-declined answer has ≥ 1 citation, or ≥ 1 web source, or `not_in_record=True`. | Tests. |
| FR-01-18 | `ScopeLabel = Literal["ALLOW_KSOR","ALLOW_CYBER_RESEARCH","DECLINE"]`; `ScopeVerdict(label, reason: str ≤ 300 chars, injection_suspected: bool, category: Literal[...] | None)`; constant `DECLINE_MESSAGE` = the exact decline text. | A test asserts the exact string, byte for byte. |
| FR-01-19 | `Decision(note_id, action: Literal["approve","change","escalate"], comment: str | None, decided_by: str, decided_at: datetime)`; `AuditEvent(event: str, at, user_id, request_id, trace_id, detail: dict)`; `LlmUsage(request_id, agent, model, input_tokens ≥0, output_tokens ≥0, cost_usd ≥0)`. | Tests. |
| FR-01-20 | Every model is `frozen` where it is a value object (Evidence, WebSource, KsorHit, LlmUsage) and forbids unknown fields (`extra="forbid"`), except `WazuhAlert`. | Tests: unknown field → error. |

### 2.3 Masking (`soc_shared.masking`)
| ID | Requirement | Acceptance |
|---|---|---|
| FR-01-30 | `MaskMap`: per-request mapping value⇄token, kinds `IP`, `USER`, `HOST`, `EMAIL`; tokens `<IP-1>`, `<USER-1>` … numbered per kind in first-seen order. | Unit tests. |
| FR-01-31 | Same value → same token within one MaskMap. Normalisation: IPs via `ipaddress` (so `::ffff:0:1` styles and leading zeros don't split); USER and HOST compared case-insensitively (Windows semantics); EMAIL lower-cased. | `Admin` and `admin` → the same `<USER-n>`. |
| FR-01-32 | `mask_text(text, map)` masks in this order (as built, T01-08): emails → `DOMAIN\user` (domain → HOST token, user → USER token) → IPv6 → IPv4 (IPv6 first so `::ffff:10.0.0.5` is one token; candidates validated by `ipaddress`; `12:30:45` and MAC addresses are not masked) → FQDNs with internal suffixes → host and user names already learned in the map (≥ 3 chars, word boundaries) — internal suffixes (`.local .lan .corp .internal .intra .home.arpa` + configurable). Public domains like `attack.mitre.org` are NOT masked. | Case tests incl. negative cases. |
| FR-01-33 | `mask_alert(alert: WazuhAlert) -> MaskedAlert`: field-aware first (known Wazuh/Windows/Linux fields → kind: e.g. `agent.name`, `agent.ip`, `data.srcip`, `data.dstip`, `data.srcuser`, `data.dstuser`, `data.win.system.computer`, `data.win.eventdata.{targetUserName, subjectUserName, workstationName, ipAddress, targetDomainName, subjectDomainName}`, `predecoder.hostname`), then `mask_text` over every remaining string value, incl. `full_log`. Alert `id`, rule fields and timestamps are not masked. `-` and empty values are left unchanged. | Golden test with Windows 4625, Linux sshd and Sysmon fixtures. |
| FR-01-34 | `ip_context`: every IP token is classified as `public`, `private <RFC1918 CIDR>`, or `special <loopback|link-local|multicast|reserved|unspecified|shared-cgnat|documentation>`. | 10.0.0.5 → `private 10.0.0.0/8`; 192.0.2.10 → `special documentation`. |
| FR-01-35 | `is_public_ip(value) -> bool` is True only for a global unicast address (`ipaddress.ip_address(v).is_global`, also excluding the documentation ranges and 100.64.0.0/10). Invalid input → False (never raises). | 10.0.0.5, 172.16.0.1, 192.168.1.1, 127.0.0.1, 169.254.1.1, ::1, fe80::1, 192.0.2.1 → False; 8.8.8.8 → True. |
| FR-01-36 | `unmask(text, map)` replaces known tokens with their values; unknown tokens are left as they are. `unmask(mask_text(x)) == x` for the masked kinds. | Round-trip property test. |
| FR-01-37 | `find_leaks(text, map) -> list[str]` returns the TOKENS whose raw values appear in `text` (it never returns the raw values, so the result is safe to log); `find_unmasked_pii(text)` returns pattern matches (IP/email) that are not tokens. Used later by the output guardrail and the trace test. | Tests. |
| FR-01-38 | `MaskMap` never appears in `repr`/`str`/logging with raw values: `repr` shows counts only; `to_storage()` returns `list[MaskEntry(token, kind, value)]` for api-gateway (encryption is feature 08). | Test: `repr(map)` contains no raw value. |

### 2.4 Settings (`soc_shared.settings`)
| ID | Requirement | Acceptance |
|---|---|---|
| FR-01-40 | `BaseServiceSettings(BaseSettings)`: `env: Literal["local","test","production"]="local"`, `log_level="INFO"`, `trace_include_sensitive_data: bool=False`; reads env vars; `.env` loading is opt-in per service (`env_file` set by the service, never in tests); secrets typed `SecretStr`. | Tests use `monkeypatch.setenv`; `repr()` hides SecretStr. |
| FR-01-41 | A validator refuses `trace_include_sensitive_data=True` when `env="production"`. | Test. |

### 2.5 Docs
| ID | Requirement | Acceptance |
|---|---|---|
| FR-01-50 | `backend/docs/LEARNING.md`: every folder/file created in 01, in simple English (what, why, which command uses it) + "uv workspace explained" + "how masking works" + the CI steps. Sections for later features are placeholders. | Naveed can read it file by file. |
| FR-01-51 | `backend/docs/CAREER-MAP.md`: table feature → Option 1 skills / Option 2 skills / 2 interview talking points; the row for 01 is filled, strictly true (home lab, simulated data). | Review by Naveed. |
| FR-01-52 | `backend/docs/architecture.md`: Mermaid diagrams of the services and of both flows (target state, from plan v2 §4–5). | It renders on GitHub. |
| FR-01-53 | `packages/soc-shared/README.md`: what it is, its public API, how to run its tests. Root `README.md` updated: project one-liner, links to the plan, the constitution, progress, LEARNING. | Review. |

## 3. Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-01-01 | No network access in any test (pytest fails a test that opens a socket — `pytest-socket` or a conftest guard; library checked in T01-01). |
| NFR-01-02 | mypy `--strict` on `soc_shared`; ruff with rules E,F,I,B,UP,S,SIM,RUF; line length 100. |
| NFR-01-03 | Coverage ≥ 90% lines for soc-shared (CI fails below it). |
| NFR-01-04 | Masking of a 50 KB alert takes < 50 ms on the dev machine (a non-flaky budget test with a generous margin, or a reported benchmark). |
| NFR-01-05 | No raw value from any fixture appears in test output or logs (assertions compare tokens; `MaskMap.repr` is safe). |
| NFR-01-06 | Fixture data uses documentation IPs (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24), RFC 1918 and invented names (`lab-ws01`, `alice.lab`) only — no real organisation data. |

## 4. Edge cases and error behaviour
- IPv4 with a port (`203.0.113.5:443`) → the IP is masked, the port is kept. CIDR (`10.0.0.0/8`) in text → kept as a range (it is not one host).
- Values that are already tokens (`<IP-1>`) → never masked again (idempotent: `mask_text(mask_text(x)) == mask_text(x)`).
- `DOMAIN\user$` (machine account) → HOST kind (the `$` suffix means a computer account).
- An empty or `-` username/hostname → unchanged; built-in principals `SYSTEM`, `LOCAL SERVICE`, `NETWORK SERVICE`, `ANONYMOUS LOGON`, `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`, `root` → kept (not personal data; escalation condition 2 needs to see a privileged account; documented in LEARNING.md).
- Invalid IP-like strings (`999.1.1.1`) → not masked, and `is_public_ip` → False.
- Non-string values in `data` (int, list, nested dict) → walked recursively; lists keep their order.

## 5. Out of scope
DB encryption of mask_map (08), the output-guardrail use of `find_leaks` (06), services, eval data (02), Docker (09), full CI (10).

## 6. Traceability
| FR | Test file / VERIFY step |
|---|---|
| FR-01-01…08 | `tests/test_repo_hygiene.py`, VERIFY §1.1–1.4 |
| FR-01-10…20 | `packages/soc-shared/tests/test_models.py`, `test_triage_note.py` |
| FR-01-30…38 | `packages/soc-shared/tests/test_masking.py`, `test_masking_properties.py`, `test_mask_alert.py` |
| FR-01-40…41 | `packages/soc-shared/tests/test_settings.py` |
| FR-01-50…53 | VERIFY §1.6 (Naveed reads) |
| NFR-01-01…06 | conftest guard, CI, `test_masking_perf.py`, review |

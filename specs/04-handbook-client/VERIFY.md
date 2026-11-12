# VERIFY — 04 handbook-client
Status: **filled (offline parts)** by Claude 2026-11-12 — the live demo (1.2–1.5) is Naveed's

## 1. Checks
| # | Where | Command | You must see |
|---|---|---|---|
| 1.1 | backend/ | `make check` | all green |
| 1.2 | T1: ../handbook | `NODE_OPTIONS="--network-family-autoselection-attempt-timeout=3000" npm run serve` | the server listening on 127.0.0.1:8080 |
| 1.3 | T2: backend/ | `make demo-handbook Q="What does event 4625 mean?" CONFIRM=haan` | `status: hits`, `gate: off`, hits with `knowledge/windows-events/event-4625` among them |
| 1.4 | T2 | `make demo-handbook Q="x"` (no CONFIRM) | refused |
| 1.5 | T2, with T1 stopped | `make demo-handbook Q="test" CONFIRM=haan` | `status: unavailable` (not "not in this record") |

## 4. Real output captured by Claude (offline)
- `make check`: `All checks passed!` · `90 files already formatted` · `Success: no issues found in 75 source files` · `Total coverage: 96.82%` · `273 passed` (ksor-client: 16 tests).
- `make demo-handbook Q="What does event 4625 mean?"` without CONFIRM → `refused: a live handbook search costs an embedding call — run with CONFIRM=haan`.
- Unreachable server (test with the connect blocked) → `status: unavailable`, `not_in_record = False`.
- No live handbook search was run by Claude.

## 5. Naveed's verdict

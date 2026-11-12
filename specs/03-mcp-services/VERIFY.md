# VERIFY — 03 mcp-services
Status: **filled** by Claude 2026-11-12 — awaiting Naveed's verification

## 1. Checks
| # | Command (from `backend/`) | You must see |
|---|---|---|
| 1.1 | `make check` | all green |
| 1.2 | `make demo-mcp` | 5 newest level≥10 alert summaries; one alert; 3 reputation results (private → not_queried, documentation → not_queried, mocked public → ok, band likely_malicious) |
| 1.3 | `make serve-wazuh-mcp` (terminal 1) | `Uvicorn running on http://127.0.0.1:8101` |
| 1.4 | `make serve-enrichment-mcp` (terminal 2) | `Uvicorn running on http://127.0.0.1:8102` |
| 1.5 | (needs your key in `.env`) `make demo-enrichment-live IP=<a public IP> CONFIRM=haan` | one real AbuseIPDB result; without `CONFIRM=haan` it refuses |

## 2. Break it on purpose
| Change | Expected |
|---|---|
| Remove the public-IP check in `enrichment_mcp/server.py` | `test_never_queries_non_public` fails |
| Add a third tool to wazuh-mcp | `test_tool_surface` fails |

## 4. Real output captured by Claude (2026-11-12, branch feat/03-mcp-services)

**`make check`**: `All checks passed!` · `83 files already formatted` · `Success: no issues found in 69 source files` ·
`Total coverage: 96.92%` · `257 passed`. The new tests: wazuh-mcp 15 · enrichment-mcp 38.

**`make demo-mcp`** (excerpt)
```
not queried: class=private 10.0.0.0/8
not queried: class=special documentation
checked ref=838c4c25 score=88
wazuh-mcp tools (read-only): ['get_alert', 'get_new_alerts']
=== get_new_alerts(since 2026-11-11, min_level 10, limit 5) ===  → count 5: EV-A034 (91844, 12), EV-A017, EV-A020, EV-A026, EV-A019
=== ip_reputation(8.8.8.8)  [AbuseIPDB MOCKED] ===
  "status": "ok", "abuse_confidence_score": 88, "handbook_band": "likely_malicious", "cached": false
(the second call for 8.8.8.8 → "cached": true, no request)
```
The logs show the IP class and a hash only. Before the fix, httpx logged `GET ...check?ipAddress=8.8.8.8`; that line is now gone.

**HTTP smoke test** (local, free): `python -m wazuh_mcp` → `Uvicorn running on http://127.0.0.1:8101`; an MCP client over HTTP →
`tools: ['get_alert', 'get_new_alerts']`, `EV-A001 rule: 60204 is_error: False`; the server was stopped by PID.

**Live demo guard:** `make demo-enrichment-live IP=8.8.8.8` → `refused: a live AbuseIPDB call needs CONFIRM=haan`.
No live AbuseIPDB call was made.

## 5. Naveed's verdict

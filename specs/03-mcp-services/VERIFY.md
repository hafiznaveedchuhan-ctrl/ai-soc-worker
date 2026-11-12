# VERIFY — 03 mcp-services
Status: **draft** (real output in §4 after T03-05)

## 1. Checks
| # | Command (from `backend/`) | You must see |
|---|---|---|
| 1.1 | `make check` | all green |
| 1.2 | `make demo-mcp` | 5 newest level≥10 alert summaries; one alert; 3 reputation results (private → not_queried, documentation → not_queried, mocked public → ok, band likely_malicious) |
| 1.3 | `make serve-wazuh-mcp` (terminal 1) | `Uvicorn running on http://127.0.0.1:8101` |
| 1.4 | `make serve-enrichment-mcp` (terminal 2) | `Uvicorn running on http://127.0.0.1:8102` |
| 1.5 | (only after your "haan") `make demo-enrichment-live IP=<a public IP>` | one real AbuseIPDB result |

## 2. Break it on purpose
| Change | Expected |
|---|---|
| Remove the public-IP check in `enrichment_mcp/server.py` | `test_never_queries_non_public` fails |
| Add a third tool to wazuh-mcp | `test_tool_surface` fails |

## 4. Real output captured by Claude
_(T03-05)_

## 5. Naveed's verdict

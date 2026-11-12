# ai-soc-worker — AI SOC Triage Copilot (Phase 3)

AI workers that answer SOC analyst questions and triage Wazuh alerts into **cited triage notes**,
using a governed SOC handbook (KSOR, over MCP), IP enrichment and trusted cyber sources.
**Read-only. Data is masked before any LLM call. A human analyst always makes the final decision.**
Home-lab learning and portfolio project; all alert data is simulated or public.

| Start here | |
|---|---|
| Where we are now | [`progress.md`](progress.md) |
| Plan of record | [`specs/00-final-plan.txt`](specs/00-final-plan.txt) |
| Rules | [`specs/constitution.md`](specs/constitution.md) · [`CLAUDE.md`](CLAUDE.md) |
| Learn the code file by file | [`backend/docs/LEARNING.md`](backend/docs/LEARNING.md) |
| Architecture | [`backend/docs/architecture.md`](backend/docs/architecture.md) · [ADRs](backend/docs/adr/README.md) |
| Career map | [`backend/docs/CAREER-MAP.md`](backend/docs/CAREER-MAP.md) |

## Quick start
```bash
cd backend
make dev            # uv sync --all-packages
make check          # lint + types + tests + coverage
make demo-masking   # see an alert before/after masking
```

## Status
Feature 01 (foundation) — see `progress.md` for the live table of features 01–10.

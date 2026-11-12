# plan — 11 live-eval
Source: `00-plan.txt` §3 (approved). ADR: ADR-0010.

## Files
- `soc_evals/pipeline.py`: the `Pipeline` protocol and `run_all` (selection, error isolation, run-wide cap). It has no agent imports.
- `soc_evals/live.py`: `AgentPipeline` (FlowResult → prediction), `build_live(settings)` and `preflight()`.
- `soc_evals/estimate.py`: the free cost estimate.
- `cli.py`: `paid` (guards and options) and `estimate`.
- `report.py`: `RunInfo.note`.
- `evals/pyproject.toml`: adds the `agent-service` dependency. There is no cycle.
- `Makefile`: `eval`, `eval-estimate` and `eval-pilot`.

## Docs checked (CLAUDE.md rule)
- **openai-agents 0.24.0** (the installed source in `.venv`, which is the exact pinned version; checked 2026-11-12):
  - `agents.testing.ScriptedModel(turns, default_usage=…)`;
  - `Runner.run`;
  - `set_trace_processors([])` turns trace export off (`agents/tracing/__init__.py:101`).
- **mcp 2.3.0** (installed source, `mcp/client/client.py:951`): `Client(target, read_timeout_seconds=…)` and `list_tools()` for the pre-flight.
- `ScriptedModel(steps, *, emit_traces, default_usage)` is at `agents/testing/model.py:256`.

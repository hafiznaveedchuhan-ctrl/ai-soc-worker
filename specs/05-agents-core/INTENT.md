# INTENT — 05 agents-core
Status: **approved** (blanket, PHR-0010) · Naveed 2026-11-12: "first finish ALL remaining coding; LLM testing later" (PHR-0012)
Goal: the 5 agents and both flows with every main Agents SDK primitive, fully testable OFFLINE with `agents.testing.ScriptedModel`.
Constraints: no paid call by Claude; live mode only with CONFIRM=haan; default model gpt-5-nano (ADR-0003); masking before any model input.
Success: both flows pass end-to-end offline; every primitive below has a test; `make demo-ask` / `make demo-triage` work in fake mode.

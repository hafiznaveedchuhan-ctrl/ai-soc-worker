# CAREER-MAP.md — what each feature proves, for two careers

Option 1 = **AI Engineer** (Agentic AI, OpenAI Agents SDK, MCP, FastAPI, Postgres/ORM, Docker, CI/CD).
Option 2 = **AI + Cybersecurity SOC Analyst**.
Every talking point is strictly true: a **home lab** with **simulated or public data**, built with an AI pair-programmer
under my specs and my review. Rows are filled only when the feature is verified.

| # | Feature | Option 1 skills | Option 2 skills | Interview talking points |
|---|---|---|---|---|
| 01 | foundation | Python 3.12 uv workspace (monorepo, one lockfile); Pydantic v2 data contracts with cross-field validators; property-based testing (Hypothesis); mypy --strict; ruff; GitHub Actions CI with SHA-pinned actions and a gitleaks secret scan; Spec-Driven Development with ADRs and prompt history records | Data minimisation before AI: masking IPs, usernames, hostnames and emails into stable tokens; RFC 1918 / RFC 5737 / CGNAT classification so only public IPs go to threat intel; keeping built-in privileged accounts visible because escalation depends on them; triage-note structure with verdict, confidence band, severity and escalation condition | 1) "I built the masking layer *before* any LLM code: a field-aware pass for known Wazuh fields plus a free-text pass, and I proved 'no raw IP or email survives' with 600 random property-test cases — not just examples." 2) "I encoded my SOC handbook's rules as types: a triage note cannot say escalate without naming an escalation-policy condition, and a verdict without a handbook citation is rejected at validation time, so the AI cannot skip the rule." |
| 02 | evals-first | — | — | — |
| 03 | mcp-services | — | — | — |
| 04 | handbook-client | — | — | — |
| 05 | agents-core | — | — | — |
| 06 | guardrails | — | — | — |
| 07 | agent-service | — | — | — |
| 08 | api-gateway | — | — | — |
| 09 | docker | — | — | — |
| 10 | ci-cd | — | — | — |

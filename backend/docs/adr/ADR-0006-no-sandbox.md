# ADR-0006 — No sandbox
- Status: **Accepted** (blanket approval 2026-11-12) · Feature 06
## Context
The Agents SDK offers sandbox agents/sessions for running generated code. The worker's job is reading alerts and the handbook and writing notes.
## Decision
No code-execution tool, no shell, no sandbox. The only side effects are: a MOCK escalation ticket behind `needs_approval=True`, and a draft
suggestion file in `backend/suggestions/`. Constitution Art. II.3.
## Consequences
Smaller attack surface (no prompt-injection-to-RCE path); some analyses (e.g. decoding Base64 in an alert) are left to the human or a future,
separately approved tool.

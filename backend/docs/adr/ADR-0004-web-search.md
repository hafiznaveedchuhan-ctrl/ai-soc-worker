# ADR-0004 — Web search: Tavily free tier wrapped in our own function tool
- Status: **Accepted** (blanket approval 2026-11-12) · Feature 05/06
## Context
Hosted tools (OpenAI `WebSearchTool`) bypass the SDK's tool-guardrail pipeline (SDK docs, checked 2026-11-12), and are billed per call against
the $10 cap. We need: domain allow-list enforced in code, PII/secret checks on queries, sanitising of untrusted pages.
## Options
1. OpenAI hosted web search — simplest; paid per call; no tool guardrails; domain filtering not under our control.
2. **Tavily `/search` (chosen)** — free 1,000 credits/month (docs.tavily.com), `include_domains` + `include_domains_mode="restrict"`,
   `search_depth="basic"` = 1 credit; called from our `web_search` function tool → tool input + output guardrails apply.
3. Brave/DuckDuckGo scraping — terms/quality issues; no domain restrict.
## Decision
`TavilySearch` port (`WEB_SEARCH_API_KEY`), trusted domains: attack.mitre.org, learn.microsoft.com, nist.gov, csrc.nist.gov, cisa.gov,
documentation.wazuh.com, github.com/wazuh/*, rfc-editor.org. Results are re-filtered in code (defence in depth), instruction-like lines removed,
each result capped, URLs recorded so the reviewer can reject any URL the tool never returned.
## Consequences
A second free account for Naveed (Tavily). No key → the research agent says web search is unavailable.

# Architecture (target state, plan v2 §4–5)

Status: feature 01 built `soc-shared` only. Everything else below is planned (features 02–10).

## Services
```mermaid
flowchart LR
  subgraph Browser["Analyst (terminal now · handbook widget later)"]
    U[analyst]
  end
  subgraph Worker["soc-worker (docker compose network)"]
    GW["api-gateway<br/>FastAPI · Auth0 JWT · roles · rate limit<br/>ONLY service with the DB"]
    AS["agent-service<br/>OpenAI Agents SDK · guardrails · sessions · tracing"]
    WZ["wazuh-mcp<br/>read-only alerts (fixture → live)"]
    EN["enrichment-mcp<br/>ip_reputation (AbuseIPDB free tier) · cache"]
    SH[["soc-shared<br/>models · masking · settings"]]
  end
  HB["handbook MCP (host)<br/>KSOR search/read/outline"]
  DB[("Neon Postgres<br/>soc_worker")]
  OAI["OpenAI API<br/>(masked data only)"]
  AB["AbuseIPDB<br/>(public IPs only)"]
  WEB["trusted domains<br/>(web search, untrusted content)"]

  U -->|Bearer JWT| GW
  GW -->|internal HTTP| AS
  GW --> DB
  AS -->|MCP| WZ
  AS -->|MCP| EN
  AS -->|MCP streamable HTTP| HB
  AS --> OAI
  AS --> WEB
  EN --> AB
  SH -.-> GW & AS & WZ & EN
```

## /ask flow (handoff pattern)
```mermaid
sequenceDiagram
  participant A as Analyst
  participant G as api-gateway
  participant S as agent-service
  participant SG as Scope Guard (input guardrail, blocking)
  participant T as Triage Agent
  participant H as SOC Handbook Agent
  participant R as Cyber Research Agent
  participant NR as Note Reviewer (output guardrail)
  A->>G: POST /ask (JWT)
  G->>G: verify JWT · rate limit · mask question · audit
  G->>S: masked question
  S->>SG: classify scope (before any tool or cost)
  alt DECLINE
    SG-->>A: exact decline text
  else ALLOW_KSOR / ALLOW_CYBER_RESEARCH
    S->>T: run
    T->>H: handoff (KSOR topic)
    T->>R: handoff (defensive, not in KSOR)
    H-->>NR: cited answer
    R-->>NR: "unverified web source" answer
    NR-->>G: pass → SSE stream / fail → safe fallback
    G-->>A: answer (stored + usage logged)
  end
```

## /triage flow (agents-as-tools pattern)
```mermaid
sequenceDiagram
  participant G as api-gateway
  participant S as agent-service
  participant W as wazuh-mcp
  participant T as Triage Agent (stays in control)
  participant E as enrichment-mcp
  participant NR as Note Reviewer
  G->>S: POST /v1/triage {alert_id}
  S->>W: get_alert(id)
  S->>S: mask_alert → MaskedAlert + MaskMap (in run context)
  S->>T: Scope Guard → run with tools
  T->>T: handbook_agent.as_tool() / research_agent.as_tool()
  T->>E: ip_reputation(<IP-n>) → unmasked in code, public IPs only
  T->>T: create_escalation_ticket (MOCK, needs_approval → human approves/rejects)
  T-->>NR: TriageNote (structured output)
  NR-->>G: note + usage + mask map (stored encrypted)
  Note over G: Analyst decides: Approve / Change / Escalate
```

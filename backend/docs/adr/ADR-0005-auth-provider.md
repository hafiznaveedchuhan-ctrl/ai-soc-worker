# ADR-0005 — Auth provider: Auth0 (free tier), verified by the gateway via JWKS
- Status: **Accepted** (blanket approval 2026-11-12; the handbook's ADR-0004 recommended Auth0) · Feature 08
## Options
1. **Auth0 (chosen)** — free tier (OIDC, PKCE for the static handbook site, RBAC roles, Actions to add a role claim); one login for site + API.
2. Clerk — great DX for Next.js, but its free tier and JWT templates are tied to its frontend SDK; the handbook site is a static export.
## Decision
Browser → Auth0 (PKCE) → access token for audience `https://soc-worker-api` → `Authorization: Bearer` → api-gateway verifies RS256 against
`https://<domain>/.well-known/jwks.json` (PyJWT `PyJWKClient`), checks `iss`, `aud`, `exp`, `sub`, reads roles from claim
`https://soc-worker/roles` (analyst | admin; none → 403), upserts `users`. `AUTH_MODE=dev` (`X-Dev-User`) for terminal tests; refused when `ENV=production`.
## Verification
`test_auth0_jwt_validation` signs real RS256 tokens with a local key and checks good / wrong aud / wrong iss / expired / wrong key / no role.

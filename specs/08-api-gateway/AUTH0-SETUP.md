# Auth0 setup — Naveed's manual steps (free tier). Do this when you want real login (not needed for dev mode).
1. auth0.com → sign up (free) → create tenant, e.g. `ai-soc-lab` (region EU or US). Your domain: `ai-soc-lab.<region>.auth0.com`.
2. **Applications → APIs → Create API**: Name `soc-worker API`, Identifier `https://soc-worker-api`, Signing algorithm **RS256**.
   In its Settings: enable **RBAC** and **Add Permissions in the Access Token**.
3. **User Management → Roles**: create roles `analyst` and `admin`; assign yourself `admin` (and a test user `analyst`).
4. **Actions → Library → Build custom → Login / Post Login**, name `add-soc-roles`, code:
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const roles = event.authorization?.roles || [];
     api.accessToken.setCustomClaim("https://soc-worker/roles", roles);
   };
   ```
   Deploy → **Actions → Triggers → post-login** → drag it into the flow → Apply.
5. **Applications → Create Application** → *Single Page Application* `ai-soc-handbook` (for the future widget): Allowed Callback URLs
   `https://ai-soc-handbook.vercel.app/callback, http://localhost:3000/callback`; Allowed Logout URLs and Web Origins `https://ai-soc-handbook.vercel.app, http://localhost:3000`.
6. In `backend/.env` (you type the values; never paste them in chat): `AUTH_MODE=auth0`, `AUTH0_DOMAIN=ai-soc-lab.<region>.auth0.com`,
   `AUTH0_AUDIENCE=https://soc-worker-api`. Keep `AUTH_MODE=dev` until then.
7. Test: Auth0 dashboard → APIs → soc-worker API → **Test** tab gives a token (machine-to-machine; add the role via the Action or test with an
   admin user token) → `curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/me`.

# ADR-0013 — Signed-in users without a SOC role may use Ask (read-only); Triage stays analyst/admin
- Status: **Accepted** (Naveed, 2026-11-21) · Feature 08 (gateway) + handbook Feature 07 (widget)

## Context
A normal reader (e.g. fatima@gmail.com) signed in through Auth0 but has no `https://soc-worker/roles`. The gateway answered 403 "no soc-worker role assigned" on `/me`, so the widget could not chat.

Naveed wants normal users to read the handbook and ask questions WITHOUT an admin assigning a role.

## Decision
- **No role means `user`, not 403.**
  - A `user` may call `/me` and `/ask`. These are read-only: handbook answers, the scope guard, masking, the budget and the rate limit all still apply.
  - `/triage`, `/notes`, `/notes/{id}` and `/notes/{id}/decision` need `analyst` or `admin` (`soc_staff`). A `user` gets 403 "this action needs the analyst role".
- **`analyst` and `admin` are unchanged.** They are still granted in Auth0 by the admin.

## Consequences
- **Anyone who can sign up can spend LLM budget through `/ask`.** The guards are:
  - the per-user rate limit;
  - the per-run budget;
  - the $9 ledger and the gateway budget (402).

  Revisit this (an invite-only sign-up, or a daily per-user cap) before a public launch.
- The widget should hide or disable the Triage tab for role `user`. That is a handbook change, for the handbook session.

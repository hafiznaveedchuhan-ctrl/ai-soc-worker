"""HTTP client to agent-service (internal network, X-Internal-Token)."""

from typing import Any

import httpx


class AgentClient:
    def __init__(self, base_url: str, token: str, http: httpx.AsyncClient | None = None) -> None:
        self._http = http or httpx.AsyncClient(base_url=base_url, timeout=180)
        self._headers = {"X-Internal-Token": token}

    async def ask(self, question: str, user_id: str, session_id: str) -> dict[str, Any]:
        r = await self._http.post(
            "/v1/ask",
            headers=self._headers,
            json={"question": question, "user_id": user_id, "session_id": session_id},
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()
        return data

    async def triage(
        self, alert_id: str, user_id: str, analyst_context: str, approve: bool
    ) -> dict[str, Any]:
        r = await self._http.post(
            "/v1/triage",
            headers=self._headers,
            json={
                "alert_id": alert_id,
                "user_id": user_id,
                "analyst_context": analyst_context,
                "approve_escalation_ticket": approve,
            },
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()
        return data

    async def healthy(self) -> bool:
        try:
            return (await self._http.get("/health")).status_code == 200
        except httpx.HTTPError:
            return False

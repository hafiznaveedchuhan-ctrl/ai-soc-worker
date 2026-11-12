"""Feature 07 — internal API over httpx ASGITransport (no network, scripted models)."""

import json
from pathlib import Path

import httpx
import pytest
from agent_service.api import create_app
from agent_service.guardrails import ReviewVerdict
from agent_service.testing import build_offline, call, msg, scripted
from agents import set_trace_processors
from soc_shared.models import DECLINE_MESSAGE, AskAnswer, ScopeVerdict

pytestmark = pytest.mark.anyio
TOKEN = "test-internal-token"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def ask_models() -> dict[str, list]:  # type: ignore[type-arg]
    return {
        "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="x"))],
        "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
        "handbook": [
            call("search_handbook", {"query": "event 4625 meaning"}, "s1"),
            msg(
                AskAnswer(
                    answer="Failed logon.",
                    scope="ALLOW_KSOR",
                    citations=["knowledge/windows-events/event-4625"],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True))],
    }


def client(tmp_path: Path, steps: dict[str, list]) -> httpx.AsyncClient:  # type: ignore[type-arg]
    set_trace_processors([])
    app, cfg, deps = build_offline(scripted(steps), tmp_path)
    api = create_app(app, cfg, deps, TOKEN)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=api), base_url="http://agent")


async def test_health_needs_no_token(tmp_path: Path) -> None:
    async with client(tmp_path, {}) as c:
        assert (await c.get("/health")).json() == {"status": "ok"}
        assert (await c.get("/ready")).status_code == 200


async def test_token_required(tmp_path: Path) -> None:
    async with client(tmp_path, {}) as c:
        body = {"question": "q", "user_id": "u", "session_id": "s"}
        assert (await c.post("/v1/ask", json=body)).status_code == 401
        assert (
            await c.post("/v1/ask", json=body, headers={"X-Internal-Token": "wrong"})
        ).status_code == 401


async def test_ask_ok_returns_usage_and_mask_entries(tmp_path: Path) -> None:
    async with client(tmp_path, ask_models()) as c:
        r = await c.post(
            "/v1/ask",
            headers={"X-Internal-Token": TOKEN},
            json={
                "question": "What does 4625 mean on 10.0.0.5?",
                "user_id": "u",
                "session_id": "s1",
            },
        )
    data = r.json()
    assert r.status_code == 200 and data["status"] == "ok"
    assert data["answer"]["citations"] == ["knowledge/windows-events/event-4625"]
    assert {"token": "<IP-1>", "kind": "IP", "value": "10.0.0.5"} in data["mask_entries"]
    assert len(data["usage"]) >= 3


async def test_ask_decline(tmp_path: Path) -> None:
    async with client(tmp_path, {}) as c:
        r = await c.post(
            "/v1/ask",
            headers={"X-Internal-Token": TOKEN},
            json={
                "question": "How do I crack NTLM hashes with hashcat?",
                "user_id": "u",
                "session_id": "s",
            },
        )
    assert r.json()["status"] == "declined" and r.json()["text"] == DECLINE_MESSAGE


async def test_ask_stream_sse(tmp_path: Path) -> None:
    async with client(tmp_path, ask_models()) as c:
        r = await c.post(
            "/v1/ask/stream",
            headers={"X-Internal-Token": TOKEN},
            json={"question": "What does event 4625 mean?", "user_id": "u", "session_id": "s"},
        )
    assert r.headers["content-type"].startswith("text/event-stream")
    events = [b for b in r.text.split("\n\n") if b.strip()]
    final = next(e for e in events if e.startswith("event: final"))
    assert json.loads(final.split("data: ", 1)[1])["citations"] == [
        "knowledge/windows-events/event-4625"
    ]
    assert events[-1].startswith("event: done")


async def test_input_validation(tmp_path: Path) -> None:
    async with client(tmp_path, {}) as c:
        r = await c.post(
            "/v1/triage",
            headers={"X-Internal-Token": TOKEN},
            json={"alert_id": "../etc/passwd", "user_id": "u"},
        )
    assert r.status_code == 422


async def test_triage_unknown_alert_is_error(tmp_path: Path) -> None:
    async with client(tmp_path, {}) as c:
        r = await c.post(
            "/v1/triage",
            headers={"X-Internal-Token": TOKEN},
            json={"alert_id": "EV-A999", "user_id": "u"},
        )
    assert r.json()["status"] == "error" and "unavailable" in r.json()["text"]

"""Feature 08 — gateway end to end: gateway → (ASGI) → real agent-service app with ScriptedModel.
SQLite in memory; dev auth and real RS256 JWTs (local key, fake JWKS). No network, no cost."""

import json
import time
from pathlib import Path
from typing import Any

import httpx
import jwt
import pytest
from agent_service.api import create_app as create_agent_app
from agent_service.guardrails import ReviewVerdict
from agent_service.testing import build_offline, call, msg, scripted
from agents import set_trace_processors
from api_gateway.agent_client import AgentClient
from api_gateway.app import create_app
from api_gateway.auth import Authenticator
from api_gateway.db import AuditLog, LlmUsageRow, MaskMapRow, TriageNoteRow, make_engine
from api_gateway.settings import GatewaySettings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import ValidationError
from soc_shared.models import AskAnswer, Evidence, ScopeVerdict, TriageNote
from sqlmodel import Session, select

pytestmark = pytest.mark.anyio
TOKEN = "internal-test"
KEY = Fernet.generate_key().decode()
DEV = {"X-Dev-User": "naveed:analyst"}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def ask_steps() -> dict[str, list[Any]]:
    return {
        "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="x"))],
        "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
        "handbook": [
            call("search_handbook", {"query": "event 4625 meaning"}, "s1"),
            msg(
                AskAnswer(
                    answer="Event 4625 on <IP-1> is a failed logon.",
                    scope="ALLOW_KSOR",
                    citations=["knowledge/windows-events/event-4625"],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True))],
    }


def triage_steps() -> dict[str, list[Any]]:
    note = TriageNote(
        alert_id="EV-A003",
        rule_id="60106",
        rule_level=3,
        time_window_start="2026-11-11T02:41:10Z",
        time_window_end="2026-11-11T02:53:40Z",
        summary="Type 10 logon for <USER-1> from <IP-2> after brute force.",
        evidence=[Evidence(fact="logon type 10", source="logonType")],
        mitre_ids=["T1078"],
        citations=["knowledge/playbooks/brute-force"],
        verdict_suggestion="TP",
        confidence=0.8,
        severity="Critical",
        escalate=True,
        escalate_condition=4,
    )
    return {
        "triage": [
            call("ask_handbook", {"input": "brute force"}, "t1"),
            call("create_escalation_ticket", {"condition": 4, "summary": "s"}, "t2"),
            msg(note),
        ],
        "handbook": [
            call("search_handbook", {"query": "brute force 4625"}, "s1"),
            msg(
                AskAnswer(
                    answer="Condition 4.",
                    scope="ALLOW_KSOR",
                    citations=["knowledge/playbooks/brute-force"],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True)), msg(ReviewVerdict(ok=True))],
    }


def gateway(
    tmp_path: Path, steps: dict[str, list[Any]], **settings_kw: Any
) -> tuple[httpx.AsyncClient, Any]:
    set_trace_processors([])
    agent_set, cfg, deps = build_offline(scripted(steps), tmp_path)
    agent_http = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_agent_app(agent_set, cfg, deps, TOKEN)),
        base_url="http://agent",
    )
    s = GatewaySettings(mask_map_key=KEY, agent_internal_token=TOKEN, **settings_kw)
    engine = make_engine("sqlite://")
    app = create_app(
        s, engine, AgentClient("http://agent", TOKEN, agent_http), settings_kw.pop("_auth", None)
    )
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://gw"), engine


def sse(text: str) -> dict[str, Any]:
    events = {}
    for block in text.split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
        if "event" in lines:
            events[lines["event"]] = lines.get("data")
    return events


async def test_health_and_me(tmp_path: Path) -> None:
    c, _ = gateway(tmp_path, {})
    async with c:
        assert (await c.get("/health")).json() == {"status": "ok"}
        assert (await c.get("/me")).status_code == 401
        me = (await c.get("/me", headers=DEV)).json()
        assert me["sub"] == "dev|naveed" and me["role"] == "analyst"
        assert (await c.get("/ready")).json()["agent_service"] is True


async def test_ask_stream_persists_usage_and_encrypted_mask_map(tmp_path: Path) -> None:
    c, engine = gateway(tmp_path, ask_steps())
    async with c:
        r = await c.post(
            "/ask", headers=DEV, json={"question": "What does event 4625 mean on 10.0.0.5?"}
        )
    ev = sse(r.text)
    final = json.loads(ev["final"])
    assert (
        final["status"] == "ok" and "10.0.0.5" in final["answer"]["answer"]
    )  # unmasked for the human
    with Session(engine) as s:
        rows = s.exec(select(MaskMapRow)).all()
        assert rows and all("10.0.0.5" not in r.value_encrypted for r in rows)  # encrypted at rest
        assert s.exec(select(LlmUsageRow)).all()
        assert any(a.event == "ask_ok" for a in s.exec(select(AuditLog)).all())


async def test_triage_note_decision_flow(tmp_path: Path) -> None:
    c, engine = gateway(tmp_path, triage_steps())
    async with c:
        r = await c.post("/triage/EV-A003", headers=DEV, json={"approve_escalation_ticket": True})
        body = r.json()
        assert r.status_code == 200 and body["status"] == "ok", body
        assert "203.0.113.45" in body["note_text"] and body["tickets"]  # unmasked for the analyst
        nid = body["note_id"]
        listed = (await c.get("/notes", headers=DEV)).json()
        assert listed[0]["id"] == nid and listed[0]["escalate"] is True
        d = (
            await c.post(
                f"/notes/{nid}/decision", headers=DEV, json={"action": "escalate", "comment": "L2"}
            )
        ).json()
        assert d["action"] == "escalate" and d["decided_by"] == "dev|naveed"
        detail = (await c.get(f"/notes/{nid}", headers=DEV)).json()
        assert (
            detail["decisions"][0]["action"] == "escalate"
            and detail["final_decision_by"] == "human"
        )
        other = {"X-Dev-User": "bob:analyst"}
        assert (await c.get(f"/notes/{nid}", headers=other)).status_code == 404  # not his note
        assert (
            await c.get(f"/notes/{nid}", headers={"X-Dev-User": "root:admin"})
        ).status_code == 200
    with Session(engine) as s:
        row = s.exec(select(TriageNoteRow)).one()
        assert "203.0.113.45" not in row.note_text and "<IP-2>" in row.note_text  # masked at rest


async def test_invalid_decision_and_alert_id(tmp_path: Path) -> None:
    c, _ = gateway(tmp_path, {})
    async with c:
        assert (
            await c.post("/notes/1/decision", headers=DEV, json={"action": "block"})
        ).status_code == 422
        assert (await c.post("/triage/bad id!", headers=DEV, json={})).status_code in (404, 422)


async def test_rate_limit(tmp_path: Path) -> None:
    c, _ = gateway(tmp_path, {}, rate_limit_per_minute=2)
    async with c:
        codes = [
            (
                await c.post("/notes/999/decision", headers=DEV, json={"action": "approve"})
            ).status_code
            for _ in range(3)
        ]
    assert codes[-1] == 429


def test_dev_auth_forbidden_in_production() -> None:
    with pytest.raises(ValidationError):
        GatewaySettings(env="production", auth_mode="dev")
    with pytest.raises(ValidationError):
        GatewaySettings(auth_mode="auth0")


# ------------------------------------------------------------------ real RS256 JWT path
class FakeJwks:
    def __init__(self, public_key: Any) -> None:
        self.public_key = public_key

    def get_signing_key_from_jwt(self, token: str | bytes) -> Any:
        return type("K", (), {"key": self.public_key})()


def token_for(private: Any, **claims: Any) -> str:
    base = {
        "iss": "https://lab.eu.auth0.com/",
        "aud": "https://soc-worker-api",
        "sub": "auth0|abc",
        "exp": int(time.time()) + 600,
        "https://soc-worker/roles": ["analyst"],
        "email": "n@lab.example",
    }
    base.update(claims)
    return jwt.encode(base, private, algorithm="RS256")


async def test_auth0_jwt_validation(tmp_path: Path) -> None:
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    authn = Authenticator(
        "auth0",
        "lab.eu.auth0.com",
        "https://soc-worker-api",
        "https://soc-worker/roles",
        FakeJwks(private.public_key()),
    )
    c, _ = gateway(tmp_path, {}, _auth=authn)
    async with c:
        ok = await c.get("/me", headers={"Authorization": f"Bearer {token_for(private)}"})
        assert ok.status_code == 200 and ok.json()["sub"] == "auth0|abc"
        for bad in (
            token_for(private, aud="other"),
            token_for(private, iss="https://evil/"),
            token_for(private, exp=int(time.time()) - 10),
        ):
            assert (
                await c.get("/me", headers={"Authorization": f"Bearer {bad}"})
            ).status_code == 401
        other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        assert (
            await c.get("/me", headers={"Authorization": f"Bearer {token_for(other_key)}"})
        ).status_code == 401
        no_role = token_for(private, **{"https://soc-worker/roles": []})
        assert (
            await c.get("/me", headers={"Authorization": f"Bearer {no_role}"})
        ).status_code == 403
        assert (
            await c.get("/me", headers=DEV)
        ).status_code == 401  # dev header ignored in auth0 mode


async def test_ask_other_users_conversation_is_forbidden(tmp_path: Path) -> None:
    steps = ask_steps()
    c, _ = gateway(tmp_path, steps)
    async with c:
        r = await c.post(
            "/ask",
            headers=DEV,
            json={"question": "What does event 4625 mean?", "conversation_id": "c1"},
        )
        assert r.status_code == 200
        r2 = await c.post(
            "/ask",
            headers={"X-Dev-User": "bob:analyst"},
            json={"question": "hi", "conversation_id": "c1"},
        )
        assert r2.status_code == 403


async def test_budget_exhausted_returns_402(tmp_path: Path) -> None:
    c, engine = gateway(tmp_path, {}, total_budget_usd=0.0001)
    with Session(engine) as s:
        s.add(
            LlmUsageRow(
                request_id="x", agent="a", model="m", input_tokens=1, output_tokens=1, cost_usd=1.0
            )
        )
        s.commit()
    async with c:
        r = await c.post("/triage/EV-A003", headers=DEV, json={})
        assert r.status_code == 402
        r2 = await c.post("/ask", headers=DEV, json={"question": "What does event 4625 mean?"})
        assert r2.status_code == 402


def test_alembic_migration_matches_models(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from alembic import command
    from alembic.config import Config

    here = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("SOC_DB_URL", f"sqlite:///{tmp_path / 'm.sqlite'}")
    cfg = Config(str(here / "alembic.ini"))
    cfg.set_main_option("script_location", str(here / "migrations"))
    command.upgrade(cfg, "head")
    command.check(cfg)  # raises if the models and the migrations disagree

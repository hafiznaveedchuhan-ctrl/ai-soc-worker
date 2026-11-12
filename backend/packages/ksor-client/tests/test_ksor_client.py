"""FR-04-01…05 — KsorClient against the fake KSOR server (in memory, offline)."""

import pytest
from ksor_client.client import KsorClient, KsorError, not_in_record, search_once
from ksor_client.models import KsorSearchResponse
from ksor_client.testing import build_fake_ksor

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_hits_carry_stable_ids_and_gate_off() -> None:
    async with KsorClient(build_fake_ksor()) as k:
        out = await k.search("What does event 4625 mean?")
    assert out.status == "hits" and out.gate == "off" and out.snapshot_token == "snap-7"
    ids = [h.stable_id for h in out.hits]
    assert "knowledge/windows-events/event-4625" in ids
    assert all(h.stable_id.startswith("knowledge/") and h.gate == "off" for h in out.hits)
    assert not not_in_record(out)


@pytest.mark.parametrize(
    ("mode", "status", "absent"),
    [
        ("abstain", "abstained", True),
        ("unavailable", "unavailable", False),
        ("unpublished", "unpublished", False),
        ("broken", "error", False),
    ],
)
async def test_three_kinds_of_no_answer_are_different(mode: str, status: str, absent: bool) -> None:
    async with KsorClient(build_fake_ksor(mode)) as k:
        out = await k.search("anything")
    assert out.status == status and out.hits == []
    assert not_in_record(out) is absent


async def test_no_matching_hits_counts_as_abstained() -> None:
    async with KsorClient(build_fake_ksor()) as k:
        out = await k.search("zzz qqq")
    assert out.status == "abstained"


async def test_snippets_are_capped() -> None:
    async with KsorClient(build_fake_ksor("long"), snippet_cap=300) as k:
        out = await k.search("brute force")
    assert out.hits and all(len(h.snippet) <= 300 for h in out.hits)
    assert out.hits[0].snippet.endswith("…[truncated]")


@pytest.mark.parametrize(("query", "k"), [("", 5), ("x" * 2001, 5), ("ok", 0), ("ok", 11)])
async def test_input_limits(query: str, k: int) -> None:
    async with KsorClient(build_fake_ksor()) as c:
        out = await c.search(query, k)
    assert out.status == "error"


async def test_read_and_outline() -> None:
    async with KsorClient(build_fake_ksor()) as k:
        doc = await k.read("event-4625")
        tree = await k.outline(limit=10)
        with pytest.raises(KsorError):
            await k.read("missing-page")
        with pytest.raises(KsorError):
            await k.read("event-4625", token_budget=50)
    assert doc.provenance.stable_id == "knowledge/windows-events/event-4625"
    assert doc.governance.trust_tier == "human-reviewed"
    assert len(tree.nodes) == 2 and tree.has_more is False


@pytest.mark.filterwarnings("ignore:A test tried to use socket.socket")
async def test_unreachable_server_is_unavailable_not_absent() -> None:
    # pytest-socket blocks the TCP connect, exactly like a stopped `npm run serve` would fail.
    out = await search_once("http://127.0.0.1:9/mcp", "event 4625", timeout=1)
    assert out.status == "unavailable" and not not_in_record(out)


async def test_search_once_happy_path() -> None:
    out = await search_once(build_fake_ksor(), "event 4625")
    assert out.status == "hits"


def test_gate_floor_maps_to_on() -> None:
    resp = KsorSearchResponse.model_validate(
        {"ok": True, "abstained": False, "gate": {"floor": 0.5}, "hits": [], "snapshot": None}
    )
    assert resp.gate != "off"


async def test_search_outside_context_manager_is_error() -> None:
    out = await KsorClient(build_fake_ksor()).search("event 4625")
    assert out.status == "error"

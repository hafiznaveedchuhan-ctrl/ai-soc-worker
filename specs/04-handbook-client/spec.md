# spec — 04 handbook-client
Status: **approved** (human:naveed, 2026-11-12) · package `backend/packages/ksor-client` (`ksor_client`)

| ID | Requirement | Acceptance |
|---|---|---|
| FR-04-01 | Pydantic models of the wire: `KsorSearchResponse` (ok, abstained, reason, gate, top_cosine, hits[slug, heading_path, content, rrf_score, provenance{corpus_id, stable_id, slug, generation, retrieved_at}, governance{status, trust_tier, …}], snapshot, note, degraded_reason), `KsorReadResponse`, `KsorOutlineResponse`; unknown extra fields are ignored (the server may add more). | Parse tests on documented-shape fixtures. |
| FR-04-02 | `KsorClient(url, timeout)` (async context manager) with `search(query, k=5)`, `read(slug, heading=None, snapshot_token=None, token_budget=None)`, `outline(node=None, depth=None, limit=50)`. Input checks match the server: query 1–2000 chars, k 1–10, token_budget 100–70000. | Tests. |
| FR-04-03 | `search()` returns `SearchOutcome(status: hits\|abstained\|unavailable\|unpublished\|error, hits: list[KsorHit], snapshot_token, gate, reason)`. `KsorHit.stable_id` = `provenance.stable_id`; `gate` = "off" when the wire says "off", else "on". Each `snippet` is capped (default 1,200 chars, marked "…[truncated]"). | Tests for each status. |
| FR-04-04 | Tool errors and transport failures become `status=error` / `unavailable` with a reason — never an exception to the caller. | Tests (fake server raises; unreachable URL). |
| FR-04-05 | `not_in_record(outcome) -> bool` is True only for `abstained` (handbook rule: "not in this record" is an answer, but unavailable is NOT absence). | Tests. |
| FR-04-06 | `make demo-handbook Q="..."` (terminal 2) prints status, gate and up to 5 hits (stable_id, heading, score, 200-char snippet). It needs `CONFIRM=haan`; without it, it refuses. | Manual. |

"""KSOR MCP wire shapes (@panaversity/ksor gateway: SEARCH_OUTPUT, READ_OUTPUT, OUTLINE_OUTPUT).

`extra="ignore"`: the server may add fields; we keep what we use and never crash on more.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _Wire(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Provenance(_Wire):
    corpus_id: str
    stable_id: str
    slug: str
    generation: int
    retrieved_at: str


class Act(_Wire):
    by: str
    at: str


class Governance(_Wire):
    status: str | None = None
    trust_tier: str
    verified: Act | None = None
    effective_from: str | None = None
    stale_after: str | None = None
    approval: Act | None = None


class Floor(_Wire):
    floor: float


class WireHit(_Wire):
    slug: str
    heading_path: str
    content: str
    rrf_score: float
    provenance: Provenance
    governance: Governance


class Snapshot(_Wire):
    corpus_id: str
    generation: int
    token: str
    expires_at: str


class KsorSearchResponse(_Wire):
    ok: bool
    abstained: bool
    reason: Literal["abstained", "unavailable", "unpublished"] | None = None
    gate: Literal["off"] | Floor
    top_cosine: float | None = None
    hits: list[WireHit]
    snapshot: Snapshot | None = None
    note: str | None = None
    degraded_reason: str | None = None


class KsorReadResponse(_Wire):
    slug: str
    title: str
    text: str
    frontmatter: str | None = None
    governance: Governance
    sections: list[str]
    provenance: Provenance
    snapshot_status: str
    next: str | None = None


class OutlineNode(_Wire):
    slug: str
    kind: str
    title: str
    heading_path: str
    position: int
    depth: int
    child_count: int
    permalink: str | None = None
    has_content: bool


class KsorOutlineResponse(_Wire):
    nodes: list[OutlineNode]
    limit: int
    offset: int
    next_offset: int | None = None
    has_more: bool

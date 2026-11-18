"""AskAnswer — the reply to an analyst question on /ask (FR-01-17)."""

import re
from typing import Any, Self

from pydantic import Field, model_validator

from soc_shared.models._base import StrictModel
from soc_shared.models.ksor import STABLE_ID_PATTERN
from soc_shared.models.note import WebSource
from soc_shared.models.scope import DECLINE_MESSAGE, ScopeLabel

_URL_IN = re.compile(r"https?://[^\s<>\"]+")


class AskAnswer(StrictModel):
    answer: str = Field(min_length=1)
    scope: ScopeLabel
    citations: list[str] = Field(
        default_factory=list,
        description="KSOR handbook stable_ids ONLY (e.g. knowledge/windows-events/event-4625). "
        "Never URLs: put web pages in web_sources.",
    )
    web_sources: list[WebSource] = Field(
        default_factory=list, description="Web pages returned by web_search (url, optional title)."
    )
    not_in_record: bool = False
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def _urls_out_of_citations(cls, data: Any) -> Any:
        """Deterministic repair (P3, 2026-11-13): the small model wrote
        "unverified web source (https://…)" into `citations` in 12 research answers, which broke the
        answer even after the retry. A URL is moved to `web_sources`; the output review still checks
        that web_search really returned it, so nothing unverified gets through."""
        if not isinstance(data, dict) or not isinstance(data.get("citations"), list):
            return data
        keep: list[Any] = []
        moved: list[dict[str, str]] = []
        for c in data["citations"]:
            m = _URL_IN.search(c) if isinstance(c, str) else None
            if m and not re.fullmatch(STABLE_ID_PATTERN, c):
                moved.append({"url": m.group(0).rstrip(").,;")})
            else:
                keep.append(c)
        if not moved:
            return data
        known = {
            w.get("url") if isinstance(w, dict) else getattr(w, "url", None)
            for w in data.get("web_sources") or []
        }
        extra = [w for w in moved if w["url"] not in known]
        return {
            **data,
            "citations": keep,
            "web_sources": [*(data.get("web_sources") or []), *extra],
        }

    @model_validator(mode="after")
    def _cite_or_abstain(self) -> Self:
        for cid in self.citations:
            if not re.fullmatch(STABLE_ID_PATTERN, cid):
                raise ValueError(f"citation is not a KSOR stable_id: {cid!r}")
        if self.scope == "DECLINE":
            if self.answer != DECLINE_MESSAGE:
                raise ValueError("a DECLINE answer must be exactly DECLINE_MESSAGE")
            return self
        if not (self.citations or self.web_sources or self.not_in_record):
            raise ValueError("answer needs a citation, a web source, or not_in_record=True")
        return self

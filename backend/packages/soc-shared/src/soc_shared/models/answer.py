"""AskAnswer — the reply to an analyst question on /ask (FR-01-17)."""

import re
from typing import Self

from pydantic import Field, model_validator

from soc_shared.models._base import StrictModel
from soc_shared.models.ksor import STABLE_ID_PATTERN
from soc_shared.models.note import WebSource
from soc_shared.models.scope import DECLINE_MESSAGE, ScopeLabel


class AskAnswer(StrictModel):
    answer: str = Field(min_length=1)
    scope: ScopeLabel
    citations: list[str] = Field(default_factory=list)
    web_sources: list[WebSource] = Field(default_factory=list)
    not_in_record: bool = False
    confidence: float = Field(ge=0.0, le=1.0)

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

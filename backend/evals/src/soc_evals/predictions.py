"""What a pipeline run produces for one eval item (FR-02-10). Stored as JSONL."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from soc_shared.models import AskAnswer, LlmUsage, ScopeLabel, TriageNote


class _Prediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str | None = None
    latency_ms: float = Field(default=0.0, ge=0)
    usage: list[LlmUsage] = Field(default_factory=list)
    output_text: str = ""  # the exact text shown to the analyst (checked for leaks)


class AlertPrediction(_Prediction):
    alert_id: str
    note: TriageNote | None = None


class ProbePrediction(_Prediction):
    probe_id: str
    scope_label: ScopeLabel | None = None
    answer: AskAnswer | None = None


def read_jsonl[P: _Prediction](path: Path, model: type[P]) -> list[P]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [model.model_validate_json(line) for line in lines if line.strip()]


def write_jsonl(path: Path, items: list[AlertPrediction] | list[ProbePrediction]) -> None:
    path.write_text("".join(i.model_dump_json() + "\n" for i in items), encoding="utf-8")

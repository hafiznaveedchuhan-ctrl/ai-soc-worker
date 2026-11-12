"""Base classes for every soc-shared model (FR-01-20)."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """A record: unknown fields are an error (catches typos and schema drift early)."""

    model_config = ConfigDict(extra="forbid")


class ValueModel(BaseModel):
    """A value object: like StrictModel, and immutable once created."""

    model_config = ConfigDict(extra="forbid", frozen=True)

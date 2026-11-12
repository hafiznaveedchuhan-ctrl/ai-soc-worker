from dataclasses import dataclass


@dataclass(frozen=True)
class Failure:
    item_id: str
    check: str
    reason: str

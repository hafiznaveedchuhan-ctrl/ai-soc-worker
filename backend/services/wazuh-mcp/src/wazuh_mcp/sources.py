"""Where alerts come from. Fixture mode serves recorded lab alerts; live mode comes later."""

import json
from datetime import datetime
from pathlib import Path
from typing import Protocol

from soc_shared.models import WazuhAlert


class AlertSource(Protocol):
    def get(self, alert_id: str) -> WazuhAlert | None: ...

    def since(self, since: datetime, min_level: int) -> list[WazuhAlert]: ...


class FixtureSource:
    """Reads every *.json in a folder once (the 40 eval alerts by default). Read-only."""

    def __init__(self, folder: Path) -> None:
        self._alerts: dict[str, WazuhAlert] = {}
        for path in sorted(folder.glob("*.json")):
            alert = WazuhAlert.model_validate(json.loads(path.read_text(encoding="utf-8")))
            self._alerts[alert.id] = alert
        if not self._alerts:
            raise FileNotFoundError(f"no alert fixtures in {folder}")

    def __len__(self) -> int:
        return len(self._alerts)

    def get(self, alert_id: str) -> WazuhAlert | None:
        return self._alerts.get(alert_id)

    def since(self, since: datetime, min_level: int) -> list[WazuhAlert]:
        hits = [
            a for a in self._alerts.values() if a.timestamp >= since and a.rule.level >= min_level
        ]
        return sorted(hits, key=lambda a: a.timestamp)


class LiveSource:
    """Placeholder: a read-only Wazuh indexer user (Phase 1 Part B/C)."""

    def __init__(self) -> None:
        raise NotImplementedError("live mode arrives after Phase 1 B/C (read-only indexer user)")

    def get(self, alert_id: str) -> WazuhAlert | None:  # pragma: no cover - never constructed
        raise NotImplementedError

    def since(self, since: datetime, min_level: int) -> list[WazuhAlert]:  # pragma: no cover
        raise NotImplementedError

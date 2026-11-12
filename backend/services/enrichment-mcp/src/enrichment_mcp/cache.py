"""TTL cache per IP and a daily request budget (UTC day). The clock is injectable for tests."""

import time
from collections.abc import Callable
from datetime import UTC, datetime

Clock = Callable[[], float]


class TtlCache[T]:
    def __init__(self, ttl_seconds: int, clock: Clock = time.time) -> None:
        self._ttl = ttl_seconds
        self._clock = clock
        self._items: dict[str, tuple[float, T]] = {}

    def get(self, key: str) -> T | None:
        hit = self._items.get(key)
        if hit is None or self._clock() - hit[0] > self._ttl:
            self._items.pop(key, None)
            return None
        return hit[1]

    def put(self, key: str, value: T) -> None:
        self._items[key] = (self._clock(), value)


class DailyBudget:
    def __init__(self, limit: int, clock: Clock = time.time) -> None:
        self._limit = limit
        self._clock = clock
        self._day = ""
        self._used = 0

    def _today(self) -> str:
        return datetime.fromtimestamp(self._clock(), UTC).date().isoformat()

    def try_spend(self) -> bool:
        if self._today() != self._day:
            self._day, self._used = self._today(), 0
        if self._used >= self._limit:
            return False
        self._used += 1
        return True

    @property
    def used(self) -> int:
        return self._used

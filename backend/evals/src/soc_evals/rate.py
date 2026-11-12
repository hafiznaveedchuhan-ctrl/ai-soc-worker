"""Rate — every metric is reported as a count AND a percent with the set size (plan A5)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    k: int
    n: int

    def __post_init__(self) -> None:
        if self.n < 0 or self.k < 0 or self.k > self.n:
            raise ValueError(f"invalid rate {self.k}/{self.n}")

    @property
    def pct(self) -> float | None:
        return None if self.n == 0 else 100.0 * self.k / self.n

    def __str__(self) -> str:
        if self.pct is None:
            return f"{self.k}/{self.n} = n/a"
        return f"{self.k}/{self.n} = {self.pct:.1f}%"

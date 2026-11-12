"""FR-02-11 — count AND percent, with the set size."""

import pytest
from soc_evals.rate import Rate


@pytest.mark.parametrize(
    ("k", "n", "text"),
    [
        (24, 25, "24/25 = 96.0%"),
        (0, 0, "0/0 = n/a"),
        (2, 3, "2/3 = 66.7%"),
        (15, 16, "15/16 = 93.8%"),
    ],
)
def test_str(k: int, n: int, text: str) -> None:
    assert str(Rate(k, n)) == text


@pytest.mark.parametrize(("k", "n"), [(3, 2), (-1, 2), (0, -1)])
def test_invalid(k: int, n: int) -> None:
    with pytest.raises(ValueError):
        Rate(k, n)


def test_pct() -> None:
    assert Rate(1, 4).pct == 25.0
    assert Rate(0, 0).pct is None

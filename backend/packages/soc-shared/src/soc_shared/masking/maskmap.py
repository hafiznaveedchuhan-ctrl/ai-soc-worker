"""MaskMap — the per-request value⇄token table (FR-01-30, 31, 38).

The map is the ONLY place where raw values live inside a worker process. Its repr shows
counts only, so printing or logging a MaskMap by mistake never leaks a value.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from soc_shared.masking.ipclass import parse_ip


class Kind(StrEnum):
    IP = "IP"
    USER = "USER"
    HOST = "HOST"
    EMAIL = "EMAIL"


@dataclass(frozen=True)
class MaskEntry:
    """One row for api-gateway's `mask_map` table (encrypted there, feature 08)."""

    token: str
    kind: Kind
    value: str = field(repr=False)  # never shown in repr


def normalise(kind: Kind, value: str) -> str:
    """The comparison key: same key ⇒ same token."""
    value = value.strip()
    if kind is Kind.IP:
        addr = parse_ip(value)
        return str(addr) if addr is not None else value
    # Windows user and host names are case-insensitive; email addresses are compared lower-case.
    return value.casefold()


class MaskMap:
    def __init__(self) -> None:
        self._token_by_key: dict[tuple[Kind, str], str] = {}
        self._value_by_token: dict[str, str] = {}
        self._kind_by_token: dict[str, Kind] = {}
        self._count: dict[Kind, int] = dict.fromkeys(Kind, 0)

    def token_for(self, kind: Kind, value: str) -> str:
        """Return the token for `value`, creating `<KIND-n>` the first time it is seen."""
        key = (kind, normalise(kind, value))
        token = self._token_by_key.get(key)
        if token is None:
            self._count[kind] += 1
            token = f"<{kind.value}-{self._count[kind]}>"
            self._token_by_key[key] = token
            self._value_by_token[token] = value.strip()
            self._kind_by_token[token] = kind
        return token

    def get_token(self, kind: Kind, value: str) -> str | None:
        return self._token_by_key.get((kind, normalise(kind, value)))

    def value_of(self, token: str) -> str | None:
        return self._value_by_token.get(token)

    def kind_of(self, token: str) -> Kind | None:
        return self._kind_by_token.get(token)

    def tokens(self, kind: Kind | None = None) -> list[str]:
        return [t for t, k in self._kind_by_token.items() if kind is None or k is kind]

    def known_values(self, kind: Kind) -> list[tuple[str, str]]:
        """(value, token) pairs of one kind — used to mask learned names in free text."""
        return [(self._value_by_token[t], t) for t in self.tokens(kind)]

    def to_storage(self) -> list[MaskEntry]:
        return [MaskEntry(t, self._kind_by_token[t], v) for t, v in self._value_by_token.items()]

    def __len__(self) -> int:
        return len(self._value_by_token)

    def __contains__(self, token: object) -> bool:
        return token in self._value_by_token

    def __repr__(self) -> str:
        counts = ", ".join(f"{k.value}={n}" for k, n in self._count.items())
        return f"MaskMap({counts})"

    __str__ = __repr__

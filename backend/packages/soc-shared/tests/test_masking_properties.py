"""INTENT S4 — property tests: no leak, round-trip and idempotence over random inputs."""

import ipaddress

from hypothesis import given, settings
from hypothesis import strategies as st
from soc_shared.masking import MaskMap, find_unmasked_pii, mask_text, unmask

words = st.text(alphabet="abcdefghij klmnop", min_size=0, max_size=20)
ipv4 = st.ip_addresses(v=4).map(str)
# IPv4-mapped IPv6 (::ffff:a.b.c.d) is the SAME address as its IPv4 form, so both get one
# token (FR-01-31) and unmask returns the first spelling seen. Round-trip is exact only for
# distinct addresses, so mapped forms are excluded here and tested on their own below.
ipv6 = (
    st.ip_addresses(v=6)
    .filter(lambda a: ipaddress.IPv6Address(a).ipv4_mapped is None)
    .map(lambda a: str(ipaddress.IPv6Address(a)))
)
emails = st.from_regex(r"[a-z]{1,8}(\.[a-z]{1,5})?@[a-z]{2,8}\.(example|lab|org)", fullmatch=True)
pii = st.one_of(ipv4, ipv6, emails)


@st.composite
def texts_with_pii(draw: st.DrawFn) -> tuple[str, list[str]]:
    values = draw(st.lists(pii, min_size=1, max_size=6))
    parts = [draw(words)]
    for v in values:
        parts += [" ", v, " ", draw(words)]
    return "".join(parts), values


@settings(max_examples=600, deadline=None)
@given(texts_with_pii())
def test_no_raw_value_survives(data: tuple[str, list[str]]) -> None:
    text, values = data
    out = mask_text(text, MaskMap())
    assert find_unmasked_pii(out) == []
    for v in values:
        assert f" {v} " not in f" {out} "


@settings(max_examples=600, deadline=None)
@given(texts_with_pii())
def test_round_trip(data: tuple[str, list[str]]) -> None:
    text, _ = data
    m = MaskMap()
    assert unmask(mask_text(text, m), m) == text


@settings(max_examples=300, deadline=None)
@given(texts_with_pii())
def test_idempotent(data: tuple[str, list[str]]) -> None:
    text, _ = data
    m = MaskMap()
    once = mask_text(text, m)
    assert mask_text(once, m) == once


@settings(max_examples=200, deadline=None)
@given(st.ip_addresses(v=4))
def test_ipv4_mapped_shares_the_ipv4_token(addr: ipaddress.IPv4Address) -> None:
    m = MaskMap()
    out = mask_text(f"a {addr} b ::ffff:{addr} c", m)
    assert out == "a <IP-1> b <IP-1> c"

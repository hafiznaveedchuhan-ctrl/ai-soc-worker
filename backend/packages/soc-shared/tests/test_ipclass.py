"""FR-01-34, FR-01-35 — IP classification; only public IPs may leave the system."""

import pytest
from soc_shared.masking.ipclass import classify_ip, is_public_ip, parse_ip


@pytest.mark.parametrize(
    ("ip", "expected"),
    [
        ("10.0.0.5", "private 10.0.0.0/8"),
        ("172.16.4.2", "private 172.16.0.0/12"),
        ("172.31.255.255", "private 172.16.0.0/12"),
        ("192.168.1.1", "private 192.168.0.0/16"),
        ("fd12:3456::1", "private fc00::/7"),
        ("127.0.0.1", "special loopback"),
        ("::1", "special loopback"),
        ("169.254.1.1", "special link-local"),
        ("fe80::1", "special link-local"),
        ("224.0.0.1", "special multicast"),
        ("0.0.0.0", "special unspecified"),
        ("100.64.0.1", "special shared-cgnat"),
        ("192.0.2.10", "special documentation"),
        ("198.51.100.77", "special documentation"),
        ("203.0.113.45", "special documentation"),
        ("2001:db8::1", "special documentation"),
        ("240.0.0.1", "special reserved"),
        ("8.8.8.8", "public"),
        ("1.1.1.1", "public"),
        ("2606:4700:4700::1111", "public"),
        ("::ffff:10.0.0.5", "private 10.0.0.0/8"),
        ("999.1.1.1", "invalid"),
        ("not-an-ip", "invalid"),
        ("", "invalid"),
    ],
)
def test_classify(ip: str, expected: str) -> None:
    assert classify_ip(ip) == expected


@pytest.mark.parametrize(
    "ip",
    [
        "10.0.0.5",
        "172.16.0.1",
        "192.168.1.1",
        "127.0.0.1",
        "169.254.1.1",
        "::1",
        "fe80::1",
        "192.0.2.1",
        "100.64.0.1",
        "999.1.1.1",
        "",
    ],
)
def test_rfc1918_not_public(ip: str) -> None:
    assert is_public_ip(ip) is False


def test_public() -> None:
    assert is_public_ip("8.8.8.8") is True


def test_parse_ip_strips_and_unwraps() -> None:
    assert str(parse_ip(" 8.8.8.8 ")) == "8.8.8.8"
    assert str(parse_ip("::ffff:8.8.8.8")) == "8.8.8.8"
    assert parse_ip("abc") is None

"""IP address classification (FR-01-34, FR-01-35).

Only a `public` address may ever leave the system (to AbuseIPDB). The decision is made with
the standard-library `ipaddress` parser plus explicit network lists, so it does not depend on
how a given Python patch release defines `is_global` for edge ranges.
"""

import ipaddress

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address

# RFC 1918 private ranges (handbook data-handling page) and the IPv6 unique-local range.
PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
]
# RFC 5737 / RFC 3849 documentation ranges — never real hosts.
DOCUMENTATION_NETWORKS = [
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("2001:db8::/32"),
]
SHARED_CGNAT = ipaddress.ip_network("100.64.0.0/10")  # RFC 6598


def parse_ip(value: str) -> IPAddress | None:
    """Parse an IP address; unwrap IPv4-mapped IPv6. Invalid input → None (never raises)."""
    try:
        addr = ipaddress.ip_address(value.strip())
    except ValueError:
        return None
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        return addr.ipv4_mapped
    return addr


def classify_ip(value: str) -> str:
    """Return "public", "private <CIDR>", "special <kind>" or "invalid"."""
    addr = parse_ip(value)
    if addr is None:
        return "invalid"
    for net in DOCUMENTATION_NETWORKS:
        if addr.version == net.version and addr in net:
            return "special documentation"
    for net in PRIVATE_NETWORKS:
        if addr.version == net.version and addr in net:
            return f"private {net}"
    if addr.version == 4 and addr in SHARED_CGNAT:
        return "special shared-cgnat"
    if addr.is_loopback:
        return "special loopback"
    if addr.is_link_local:
        return "special link-local"
    if addr.is_multicast:
        return "special multicast"
    if addr.is_unspecified:
        return "special unspecified"
    if addr.is_reserved or not addr.is_global:
        return "special reserved"
    return "public"


def is_public_ip(value: str) -> bool:
    """True only for a global unicast address that may be sent to a threat-intel API."""
    return classify_ip(value) == "public"

"""Field-aware masking of a whole Wazuh alert (FR-01-11, 12, 33, 34).

Pass 1 masks the fields whose meaning we know (agent.name is a host, data.srcip is an IP …)
and drops secret fields. Pass 2 runs `mask_text` over every other string, so names learned
in pass 1 are also masked inside free text such as `full_log`.
"""

import json
from collections.abc import Callable
from typing import Any

from soc_shared.masking.ipclass import classify_ip, parse_ip
from soc_shared.masking.maskmap import Kind, MaskMap
from soc_shared.masking.patterns import SECRET_KEY_RE, WELL_KNOWN_PRINCIPALS
from soc_shared.masking.text import mask_domain_user, mask_text
from soc_shared.models.alert import MaskedAlert, WazuhAlert

# Field kind by the LAST key of its path (case-insensitive) — Wazuh, Windows, Sysmon, Linux.
KEY_KINDS: dict[str, Kind] = {
    **dict.fromkeys(
        [
            "ip",
            "srcip",
            "dstip",
            "src_ip",
            "dst_ip",
            "ipaddress",
            "sourceip",
            "destinationip",
            "client_ip",
            "remote_ip",
        ],
        Kind.IP,
    ),
    **dict.fromkeys(
        [
            "srcuser",
            "dstuser",
            "user",
            "username",
            "targetusername",
            "subjectusername",
            "uname",
            "uname_after",
            "accountname",
        ],
        Kind.USER,
    ),
    **dict.fromkeys(
        [
            "hostname",
            "computer",
            "workstationname",
            "sourcehostname",
            "destinationhostname",
            "targetdomainname",
            "subjectdomainname",
        ],
        Kind.HOST,
    ),
}
# Fields whose last key is too generic ("name") — matched by full path.
PATH_KINDS: dict[str, Kind] = {"agent.name": Kind.HOST, "manager.name": Kind.HOST}
# Top-level keys that are never masked (identifiers, rule metadata, time).
UNMASKED_TOP_LEVEL = frozenset({"id", "timestamp", "rule"})


def _mask_field(kind: Kind, value: str, mask_map: MaskMap) -> str:
    if value.strip().casefold() in WELL_KNOWN_PRINCIPALS:
        return value
    if kind is Kind.IP:
        return mask_map.token_for(Kind.IP, value) if parse_ip(value) else mask_text(value, mask_map)
    if kind is Kind.USER:
        if "\\" in value:
            domain, _, user = value.partition("\\")
            return mask_domain_user(domain, user, mask_map)
        if value.endswith("$"):
            return mask_map.token_for(Kind.HOST, value[:-1]) + "$"
    return mask_map.token_for(kind, value)


def _walk(node: Any, path: str, fn: Callable[[str, Any], Any]) -> Any:
    if isinstance(node, dict):
        return {k: fn(f"{path}.{k}" if path else k, v) for k, v in node.items()}
    if isinstance(node, list):
        return [fn(path, v) for v in node]
    return node


def mask_alert(alert: WazuhAlert, mask_map: MaskMap) -> MaskedAlert:
    raw: dict[str, Any] = alert.model_dump(mode="json", exclude_none=True)
    dropped: list[str] = []

    def pass1(path: str, value: Any) -> Any:
        key = path.rsplit(".", 1)[-1]
        if isinstance(value, dict | list):
            return _walk(value, path, pass1)
        if SECRET_KEY_RE.match(key):
            dropped.append(path)
            return None
        kind = PATH_KINDS.get(path) or KEY_KINDS.get(key.casefold())
        if kind is not None and isinstance(value, str):
            return _mask_field(kind, value, mask_map)
        return value

    def pass2(path: str, value: Any) -> Any:
        if isinstance(value, dict | list):
            return _walk(value, path, pass2)
        return mask_text(value, mask_map) if isinstance(value, str) else value

    kept = {k: v for k, v in raw.items() if k in UNMASKED_TOP_LEVEL}
    rest = {k: v for k, v in raw.items() if k not in UNMASKED_TOP_LEVEL}
    rest = _walk(rest, "", pass1)
    rest = _strip_none(_walk(rest, "", pass2))

    payload = {**kept, **rest}
    # Only the IP tokens that occur in THIS alert (one MaskMap can serve a whole request).
    present = json.dumps(payload)
    ip_context = {
        t: classify_ip(mask_map.value_of(t) or "") for t in mask_map.tokens(Kind.IP) if t in present
    }
    return MaskedAlert(
        alert_id=alert.id,
        rule_id=alert.rule.id,
        rule_level=alert.rule.level,
        payload=payload,
        ip_context=ip_context,
        dropped_fields=dropped,
    )


def _strip_none(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _strip_none(v) for k, v in node.items() if v is not None}
    if isinstance(node, list):
        return [_strip_none(v) for v in node]
    return node

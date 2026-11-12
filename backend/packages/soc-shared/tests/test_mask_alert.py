"""FR-01-11, 12, 33, 34 — field-aware masking of whole alerts (golden checks)."""

import json
from typing import Any

from soc_shared.masking import MaskMap, find_unmasked_pii, mask_alert
from soc_shared.models import WazuhAlert

RAW_VALUES = [
    "10.10.20.15",
    "203.0.113.45",
    "192.168.56.20",
    "198.51.100.77",
    "203.0.113.80",
    "lab-ws01",
    "lab-srv02",
    "LAB-KALI",
    "lab-wazuh",
    "alice",
    "bob@lab.example",
    "Winter2026!",
]


def masked(raw: dict[str, Any], m: MaskMap | None = None) -> tuple[Any, MaskMap]:
    m = m or MaskMap()
    return mask_alert(WazuhAlert.model_validate(raw), m), m


def assert_clean(payload: dict[str, Any]) -> None:
    text = json.dumps(payload)
    for value in RAW_VALUES:
        assert value.lower() not in text.lower(), "a raw value survived masking"
    assert find_unmasked_pii(text) == []


def test_windows_4625(win_4625: dict[str, Any]) -> None:
    out, _ = masked(win_4625)
    ed = out.payload["data"]["win"]["eventdata"]
    assert ed["targetUserName"] == "<USER-1>"
    assert ed["ipAddress"] == "<IP-2>"
    assert ed["subjectUserName"] == "<HOST-1>$"  # machine account of the agent host
    assert out.payload["agent"]["name"] == "<HOST-1>"
    assert "Account Name: <USER-1>" in out.payload["full_log"]
    assert out.ip_context == {"<IP-1>": "private 10.0.0.0/8", "<IP-2>": "special documentation"}
    assert (out.alert_id, out.rule_id, out.rule_level) == ("1731390000.100001", "60122", 5)
    assert ed["logonType"] == "3" and ed["status"] == "0xc000006d"  # evidence fields kept
    assert_clean(out.payload)


def test_rule_and_ids_untouched(win_4625: dict[str, Any]) -> None:
    out, _ = masked(win_4625)
    assert out.payload["rule"]["id"] == "60122"
    assert out.payload["id"] == "1731390000.100001"


def test_linux_sshd_keeps_root(linux_sshd: dict[str, Any]) -> None:
    out, _ = masked(linux_sshd)
    assert out.payload["data"] == {"srcip": "<IP-2>", "srcport": "40122", "dstuser": "root"}
    assert out.payload["full_log"].endswith("Failed password for root from <IP-2> port 40122 ssh2")
    assert out.payload["predecoder"]["hostname"] == "<HOST-1>"
    assert_clean(out.payload)


def test_sysmon_drops_password_keeps_hash(sysmon_1: dict[str, Any]) -> None:
    out, _ = masked(sysmon_1)
    ed = out.payload["data"]["win"]["eventdata"]
    assert "password" not in ed
    assert out.dropped_fields == ["data.win.eventdata.password"]
    assert ed["hashes"].startswith("SHA256=9F86D0")  # IOC kept (INTENT Q1)
    assert ed["user"] == "<HOST-3>\\<USER-1>"
    assert "http://<IP-" in ed["commandLine"] and "<EMAIL-1>" in ed["commandLine"]
    assert ed["image"].endswith("powershell.exe")
    assert_clean(out.payload)


def test_one_map_across_alerts_is_consistent(
    win_4625: dict[str, Any], sysmon_1: dict[str, Any]
) -> None:
    a, m = masked(win_4625)
    b, _ = masked(sysmon_1, m)
    assert a.payload["agent"]["name"] == b.payload["agent"]["name"]
    assert set(b.ip_context) <= set(m.tokens())
    assert "<IP-2>" not in b.ip_context  # only IPs present in THIS alert


def test_empty_and_dash_values_unchanged(win_4625: dict[str, Any]) -> None:
    win_4625["data"]["win"]["eventdata"]["workstationName"] = "-"
    win_4625["data"]["win"]["eventdata"]["subjectUserName"] = ""
    out, _ = masked(win_4625)
    ed = out.payload["data"]["win"]["eventdata"]
    assert ed["workstationName"] == "-" and ed["subjectUserName"] == ""


def test_nested_lists_and_non_strings(win_4625: dict[str, Any]) -> None:
    win_4625["data"]["extra"] = {"ips": ["10.0.0.7", 42, {"srcip": "10.0.0.8"}], "n": 3}
    out, _ = masked(win_4625)
    extra = out.payload["data"]["extra"]
    assert extra["ips"][0].startswith("<IP-") and extra["ips"][1] == 42
    assert extra["ips"][2]["srcip"].startswith("<IP-") and extra["n"] == 3


def test_bad_ip_in_ip_field_falls_back_to_text(win_4625: dict[str, Any]) -> None:
    win_4625["data"]["win"]["eventdata"]["ipAddress"] = "::ffff:203.0.113.45 (mapped)"
    out, _ = masked(win_4625)
    assert out.payload["data"]["win"]["eventdata"]["ipAddress"].startswith("<IP-")

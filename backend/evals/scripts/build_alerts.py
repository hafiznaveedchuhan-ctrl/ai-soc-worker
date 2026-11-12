"""Build the eval alerts, labels.csv and context.csv (FR-02-01…04, ADR-0009).

Every alert is SYNTHETIC lab data: documentation IPs (RFC 5737), RFC 1918 and invented `lab-*`
names. Every rule id / level / MITRE id comes from the handbook page named in `rule_source`
(read only). Labels are UNVERIFIED drafts until Naveed fills `verified_by`.

Field paths follow the Wazuh eventchannel decoder convention (`data.win.system.*`,
`data.win.eventdata.<camelCase Windows XML name>`). The 1102 `logFileCleared` path is
best-effort and is to be re-checked against a live lab alert (Phase 1 B/C).

Severity is computed with the handbook severity model (rules-map/severity-model):
Critical = condition 1, 3 or 4, or 6/7 on a domain controller; High = level 10–11 or
condition 2, 5, 6, 7; Medium = level 7–9; Low = level 3–6.

Run from backend/: `uv run python evals/scripts/build_alerts.py`.
"""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[2]
DATA = BACKEND / "evals/data"

WIN_RULES = "knowledge/wazuh/windows-rules-reference"
SSH_RULES = "knowledge/wazuh/sshd-rules-reference"
USERADD = "knowledge/linux-auth/new-user-useradd"
FIM = "knowledge/playbooks/fim-or-malware-alert"

HOSTS = {
    "lab-ws01": "10.10.20.15",
    "lab-ws02": "10.10.20.16",
    "lab-ws03": "10.10.20.17",
    "lab-srv02": "192.168.56.20",
    "lab-srv03": "10.10.20.33",
    "lab-srv04": "10.20.30.40",
    "lab-dc01": "10.10.10.5",
    "lab-sql01": "10.10.30.11",
    "lab-bkp01": "10.10.30.40",
    "lab-web01": "10.10.40.10",
    "lab-fw01": "10.10.0.1",
    # OTRF Security-Datasets lab hosts (public, simulated "theshire.local" lab; MIT licence)
    "WORKSTATION5": "",
    "WORKSTATION6": "",
}
RULESET = "https://github.com/wazuh/wazuh/blob/v4.14.10/ruleset/rules/"
OTRF = "OTRF Security-Datasets (MIT, (c) 2021 Open Threat Research Forge) datasets/atomic/windows/"
PORT_SCAN = "knowledge/playbooks/port-scan"
PSH = "knowledge/playbooks/suspicious-powershell"
AGENT_IDS = {name: f"{i:03d}" for i, name in enumerate(HOSTS, start=1)}


@dataclass
class Spec:
    aid: str
    playbook: str
    rule: tuple[str, int, str, list[str], list[str]]  # id, level, description, groups, mitre
    host: str
    ts: str
    data: dict[str, Any]
    full_log: str
    verdict: str
    conditions: list[int]  # first = primary escalation condition; [] = escalate no
    mitre: list[str]
    pages: list[str]
    rule_source: str
    rationale: str
    context: str = ""
    location: str = "EventChannel"
    decoder: str = "windows_eventchannel"
    extra: dict[str, Any] = field(default_factory=dict)
    source: str = "SYNTHETIC"
    source_ref: str = ""


def severity(level: int, conditions: list[int], host: str) -> str:
    on_dc = host.startswith("lab-dc")
    if set(conditions) & {1, 3, 4} or (on_dc and set(conditions) & {6, 7}):
        return "Critical"
    if 10 <= level <= 11 or set(conditions) & {2, 5, 6, 7, 8}:
        return "High"
    if 7 <= level <= 9:
        return "Medium"
    return "Low"


def win(event_id: str, host: str, eventdata: dict[str, str], ts: str) -> dict[str, Any]:
    computer = f"{host}.lab.local" if host.startswith("lab-") else f"{host}.theshire.local"
    return {
        "win": {
            "system": {
                "eventID": event_id,
                "computer": computer,
                "channel": "Security" if event_id not in {"7045"} else "System",
                "providerName": "Microsoft-Windows-Security-Auditing"
                if event_id != "7045"
                else "Service Control Manager",
                "systemTime": ts,
            },
            "eventdata": eventdata,
        }
    }


SPECS: list[Spec] = [
    # ------------------------------------------------------------------ brute-force
    Spec(
        "EV-A001",
        "brute-force",
        (
            "60204",
            10,
            "Multiple Windows Logon Failures",
            ["windows", "authentication_failures"],
            ["T1110"],
        ),
        "lab-ws01",
        "2026-11-11T02:41:10Z",
        win(
            "4625",
            "lab-ws01",
            {
                "targetUserName": "alice",
                "targetDomainName": "LAB",
                "ipAddress": "203.0.113.45",
                "logonType": "3",
                "status": "0xc000006d",
                "subStatus": "0xc000006a",
                "workstationName": "LAB-KALI",
            },
            "2026-11-11T02:41:10Z",
        ),
        "8 failed network logons (4625, Logon Type 3, 0xC000006A) for LAB\\alice from 203.0.113.45 in 4 minutes.",
        "TP",
        [],
        ["T1110", "T1110.001"],
        ["knowledge/playbooks/brute-force", "knowledge/windows-events/event-4625", WIN_RULES],
        WIN_RULES,
        "Rule 60204 = 8 failures in 240 s from one ipAddress; 0xC000006A = bad password; external source; "
        "no success follows, target not privileged → TP, no escalation condition; level 10 → High.",
    ),
    Spec(
        "EV-A002",
        "brute-force",
        (
            "5763",
            10,
            "sshd: brute force trying to get access to the system. Authentication failed.",
            ["syslog", "sshd", "authentication_failures"],
            ["T1110"],
        ),
        "lab-srv02",
        "2026-11-11T03:05:44Z",
        {"srcip": "198.51.100.77", "srcport": "40122", "dstuser": "root"},
        "Nov 11 03:05:44 lab-srv02 sshd[2211]: Failed password for root from 198.51.100.77 port 40122 ssh2",
        "TP",
        [2],
        ["T1110", "T1110.001"],
        [
            "knowledge/playbooks/brute-force",
            "knowledge/linux-auth/ssh-failed-password",
            SSH_RULES,
            "knowledge/rules-map/escalation-policy",
        ],
        SSH_RULES,
        "Rule 5763 = 8 failures in 120 s from one IP; target is root (privileged) → escalation condition 2; "
        "level 10 → High. NOTE for Naveed: condition 2 names Windows accounts; root treated as privileged.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    Spec(
        "EV-A017",
        "brute-force",
        (
            "60204",
            10,
            "Multiple Windows Logon Failures",
            ["windows", "authentication_failures"],
            ["T1110"],
        ),
        "lab-srv03",
        "2026-11-11T04:12:03Z",
        win(
            "4625",
            "lab-srv03",
            {
                "targetUserName": "Administrator",
                "targetDomainName": "LAB-SRV03",
                "ipAddress": "203.0.113.61",
                "logonType": "3",
                "status": "0xc000006d",
                "subStatus": "0xc000006a",
                "workstationName": "-",
            },
            "2026-11-11T04:12:03Z",
        ),
        "11 failed network logons for the built-in Administrator from 203.0.113.61 in 3 minutes.",
        "TP",
        [2],
        ["T1110", "T1110.001"],
        [
            "knowledge/playbooks/brute-force",
            "knowledge/rules-map/escalation-policy",
            "knowledge/windows-events/event-4625",
        ],
        WIN_RULES,
        "Brute force (60204) against the built-in Administrator → escalation condition 2 (privileged target); High.",
    ),
    Spec(
        "EV-A020",
        "brute-force",
        (
            "5712",
            10,
            "sshd: brute force trying to get access to the system. Non existent user.",
            ["syslog", "sshd", "authentication_failures"],
            ["T1110"],
        ),
        "lab-web01",
        "2026-11-11T05:20:31Z",
        {"srcip": "198.51.100.66", "srcport": "51022", "srcuser": "oracle"},
        "Nov 11 05:20:31 lab-web01 sshd[901]: Invalid user oracle from 198.51.100.66 port 51022",
        "TP",
        [],
        ["T1110"],
        ["knowledge/playbooks/brute-force", "knowledge/linux-auth/ssh-invalid-user", SSH_RULES],
        SSH_RULES,
        "Rule 5712 = 8 non-existent-user attempts in 120 s from one external IP; no success; no privileged real "
        "account → TP, no escalation condition; level 10 → High.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    # ------------------------------------------------------------------ success-after-failures
    Spec(
        "EV-A003",
        "success-after-failures",
        ("60106", 3, "Windows Logon Success", ["windows", "authentication_success"], ["T1078"]),
        "lab-ws01",
        "2026-11-11T02:53:40Z",
        win(
            "4624",
            "lab-ws01",
            {
                "targetUserName": "alice",
                "targetDomainName": "LAB",
                "ipAddress": "203.0.113.45",
                "logonType": "10",
                "workstationName": "LAB-KALI",
            },
            "2026-11-11T02:53:40Z",
        ),
        "Successful RemoteInteractive logon (Type 10) for LAB\\alice from 203.0.113.45.",
        "TP",
        [4],
        ["T1078", "T1110"],
        [
            "knowledge/playbooks/success-after-failures",
            "knowledge/rules-map/escalation-policy",
            "knowledge/windows-events/event-4624",
        ],
        WIN_RULES,
        "4624 for the same account and source 12 minutes after rule 60204 (EV-A001) → escalation condition 4; "
        "condition 4 → Critical.",
        context="Wazuh rule 60204 fired for the same account and source at 02:41 UTC (alert EV-A001).",
    ),
    Spec(
        "EV-A004",
        "success-after-failures",
        (
            "5715",
            3,
            "sshd: authentication success.",
            ["syslog", "sshd", "authentication_success"],
            ["T1078", "T1021"],
        ),
        "lab-srv02",
        "2026-11-11T09:14:12Z",
        {"srcip": "198.51.100.23", "srcport": "60211", "dstuser": "bob"},
        "Nov 11 09:14:12 lab-srv02 sshd[3120]: Accepted password for bob from 198.51.100.23 port 60211 ssh2",
        "needs_info",
        [],
        ["T1078"],
        ["knowledge/playbooks/success-after-failures", "knowledge/linux-auth/ssh-accepted"],
        SSH_RULES,
        "Success after only 5 earlier failures (below 8, no 5763/60204) → condition 4 not met; whether "
        "198.51.100.23 is bob's normal location is unknown → needs-info; level 3 → Low, so not condition 8.",
        context="5 failed passwords for bob from the same IP between 09:02 and 09:10 UTC; no brute-force rule fired.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    # ------------------------------------------------------------------ lateral movement (condition 5)
    Spec(
        "EV-A018",
        "success-after-failures",
        ("60106", 3, "Windows Logon Success", ["windows", "authentication_success"], ["T1078"]),
        "lab-srv03",
        "2026-11-11T06:31:09Z",
        win(
            "4624",
            "lab-srv03",
            {
                "targetUserName": "alice",
                "targetDomainName": "LAB",
                "ipAddress": "10.10.20.15",
                "logonType": "3",
                "workstationName": "LAB-WS01",
            },
            "2026-11-11T06:31:09Z",
        ),
        "Network logon (Type 3) for LAB\\alice on lab-srv03 from lab-ws01.",
        "TP",
        [5],
        ["T1078"],
        ["knowledge/rules-map/escalation-policy", "knowledge/windows-events/event-4624"],
        WIN_RULES,
        "Same account with Type 3 logons to 4 hosts in 6 minutes → lateral-movement signs, escalation "
        "condition 5 → High.",
        context="LAB\\alice also logged on with Type 3 to lab-srv02, lab-sql01 and lab-bkp01 between 06:25 and 06:31 UTC.",
    ),
    # ------------------------------------------------------------------ account-lockout-storm
    Spec(
        "EV-A005",
        "account-lockout-storm",
        (
            "60115",
            9,
            "User account locked out (multiple login errors)",
            ["windows", "account_changed"],
            ["T1110", "T1531"],
        ),
        "lab-dc01",
        "2026-11-11T07:02:55Z",
        win(
            "4740",
            "lab-dc01",
            {
                "targetUserName": "dave",
                "targetDomainName": "LAB",
                "subjectUserName": "LAB-DC01$",
                "callerComputerName": "LAB-WS03",
            },
            "2026-11-11T07:02:55Z",
        ),
        "A user account was locked out: LAB\\dave, caller computer LAB-WS03.",
        "TP",
        [],
        ["T1110", "T1110.003"],
        [
            "knowledge/playbooks/account-lockout-storm",
            "knowledge/windows-events/event-4740",
            "knowledge/mitre/t1110-003-password-spraying",
        ],
        WIN_RULES,
        "One of 31 lockouts in 10 minutes, all from caller LAB-WS03 across different accounts → password "
        "spraying pattern → TP; no escalation condition; level 9 → Medium.",
        context="31 lockouts (4740) for 31 different accounts in 10 minutes, all with caller computer LAB-WS03.",
    ),
    Spec(
        "EV-A006",
        "account-lockout-storm",
        (
            "60115",
            9,
            "User account locked out (multiple login errors)",
            ["windows", "account_changed"],
            ["T1110", "T1531"],
        ),
        "lab-dc01",
        "2026-11-11T10:40:18Z",
        win(
            "4740",
            "lab-dc01",
            {
                "targetUserName": "carol",
                "targetDomainName": "LAB",
                "subjectUserName": "LAB-DC01$",
                "callerComputerName": "LAB-WS02",
            },
            "2026-11-11T10:40:18Z",
        ),
        "A user account was locked out: LAB\\carol, caller computer LAB-WS02.",
        "needs_info",
        [],
        ["T1110"],
        [
            "knowledge/playbooks/account-lockout-storm",
            "knowledge/windows-events/event-4740",
            "knowledge/false-positives/expired-or-mistyped-passwords",
        ],
        WIN_RULES,
        "A single lockout from the user's usual workstation; failure codes and help-desk status unknown → "
        "needs-info; level 9 → Medium, so not condition 8.",
    ),
    # ------------------------------------------------------------------ added-to-admin-group
    Spec(
        "EV-A007",
        "added-to-admin-group",
        ("60154", 12, "Administrators Group Changed", ["windows", "group_changed"], ["T1484"]),
        "lab-ws02",
        "2026-11-11T03:22:07Z",
        win(
            "4732",
            "lab-ws02",
            {
                "targetUserName": "Administrators",
                "targetSid": "S-1-5-32-544",
                "memberName": "-",
                "memberSid": "S-1-5-21-1111-2222-3333-1145",
                "subjectUserName": "alice",
                "subjectDomainName": "LAB",
            },
            "2026-11-11T03:22:07Z",
        ),
        "A member was added to a security-enabled local group: Administrators; member SID ...-1145; by LAB\\alice.",
        "TP",
        [6, 1],
        ["T1098", "T1484"],
        [
            "knowledge/playbooks/added-to-admin-group",
            "knowledge/windows-events/event-4732",
            "knowledge/windows-events/event-4720",
        ],
        WIN_RULES,
        "Account created 4 minutes earlier (4720) added to Administrators at 03:22 by a non-admin user, no "
        "ticket → TP; condition 6 (primary) and condition 1 (level 12) → Critical.",
        context="The member SID ...-1145 is the local account helpdesk2, created at 03:18 UTC (event 4720) by LAB\\alice. No change ticket.",
    ),
    Spec(
        "EV-A008",
        "added-to-admin-group",
        ("60154", 12, "Administrators Group Changed", ["windows", "group_changed"], ["T1484"]),
        "lab-dc01",
        "2026-11-08T23:15:40Z",
        win(
            "4732",
            "lab-dc01",
            {
                "targetUserName": "Administrators",
                "targetSid": "S-1-5-32-544",
                "memberName": "CN=erin,OU=Admins,DC=lab,DC=local",
                "memberSid": "S-1-5-21-1111-2222-3333-1201",
                "subjectUserName": "adm-frank",
                "subjectDomainName": "LAB",
            },
            "2026-11-08T23:15:40Z",
        ),
        "A member was added to a security-enabled local group: Administrators; member erin; by LAB\\adm-frank.",
        "benign_TP",
        [6, 1],
        ["T1098", "T1484"],
        [
            "knowledge/playbooks/added-to-admin-group",
            "knowledge/false-positives/admin-maintenance-windows",
            "knowledge/rules-map/escalation-policy",
        ],
        WIN_RULES,
        "Inside the Sunday window with a matching ticket → benign TP, BUT maintenance never suppresses an "
        "admin-group addition or level ≥ 12 → still escalate (condition 6, also 1); on a DC → Critical.",
        context="Change ticket CHG-2001: adm-frank adds erin to Administrators on lab-dc01 during the Sunday window.",
    ),
    # ------------------------------------------------------------------ new-local-account
    Spec(
        "EV-A009",
        "new-local-account",
        (
            "60109",
            8,
            "User account enabled or created",
            ["windows", "adduser", "account_changed"],
            ["T1098"],
        ),
        "lab-ws02",
        "2026-11-11T03:18:02Z",
        win(
            "4720",
            "lab-ws02",
            {
                "targetUserName": "helpdesk2",
                "targetDomainName": "LAB-WS02",
                "subjectUserName": "alice",
                "subjectDomainName": "LAB",
            },
            "2026-11-11T03:18:02Z",
        ),
        "A user account was created: helpdesk2 on LAB-WS02 by LAB\\alice.",
        "TP",
        [],
        ["T1136.001", "T1098"],
        [
            "knowledge/playbooks/new-local-account",
            "knowledge/windows-events/event-4720",
            "knowledge/mitre/t1136-001-local-account",
        ],
        WIN_RULES,
        "Local account created at 03:18 by a normal user account, no change ticket → TP (persistence); not yet "
        "in Administrators in this alert → no condition; level 8 → Medium.",
        context="No change ticket for lab-ws02. LAB\\alice is not an IT admin.",
    ),
    Spec(
        "EV-A010",
        "new-local-account",
        ("5902", 8, "New user added to the system.", ["syslog", "adduser"], ["T1136"]),
        "lab-srv02",
        "2026-11-11T03:09:51Z",
        {"dstuser": "backupx", "uid": "1007"},
        "Nov 11 03:09:51 lab-srv02 useradd[3302]: new user: name=backupx, UID=1007, GID=1007, home=/home/backupx",
        "TP",
        [],
        ["T1136", "T1136.001"],
        ["knowledge/playbooks/new-local-account", USERADD],
        USERADD,
        "Account created at 03:09 by root via sudo from deploy's session, no ticket → TP (persistence); "
        "level 8 → Medium; no escalation condition in this alert.",
        context="Created by root via sudo from the SSH session of user deploy; no change ticket.",
        location="/var/log/auth.log",
        decoder="useradd",
    ),
    # ------------------------------------------------------------------ new-service-or-scheduled-task
    Spec(
        "EV-A011",
        "new-service-or-scheduled-task",
        ("61138", 5, "New Windows Service Created", ["windows", "windows_system"], ["T1543.003"]),
        "lab-dc01",
        "2026-11-11T03:41:26Z",
        win(
            "7045",
            "lab-dc01",
            {
                "serviceName": "WinUpdSvc",
                "imagePath": "C:\\Users\\Public\\svc.exe",
                "serviceType": "user mode service",
                "startType": "auto start",
                "accountName": "LocalSystem",
            },
            "2026-11-11T03:41:26Z",
        ),
        "A service was installed: WinUpdSvc, C:\\Users\\Public\\svc.exe, auto start, LocalSystem.",
        "TP",
        [7],
        ["T1543.003"],
        [
            "knowledge/playbooks/new-service-or-scheduled-task",
            "knowledge/windows-events/event-7045",
            "knowledge/mitre/t1543-003-windows-service",
        ],
        WIN_RULES,
        "New auto-start service from C:\\Users\\Public on a domain controller, no ticket → TP; condition 7 "
        "on a DC → Critical.",
    ),
    Spec(
        "EV-A012",
        "new-service-or-scheduled-task",
        ("61138", 5, "New Windows Service Created", ["windows", "windows_system"], ["T1543.003"]),
        "lab-srv03",
        "2026-11-08T22:47:10Z",
        win(
            "7045",
            "lab-srv03",
            {
                "serviceName": "Wazuh",
                "imagePath": "C:\\Program Files (x86)\\ossec-agent\\wazuh-agent.exe",
                "serviceType": "user mode service",
                "startType": "auto start",
                "accountName": "LocalSystem",
            },
            "2026-11-08T22:47:10Z",
        ),
        "A service was installed: Wazuh, C:\\Program Files (x86)\\ossec-agent\\wazuh-agent.exe.",
        "benign_TP",
        [],
        ["T1543.003"],
        [
            "knowledge/playbooks/new-service-or-scheduled-task",
            "knowledge/false-positives/admin-maintenance-windows",
        ],
        WIN_RULES,
        "Agent upgrade inside the Sunday window with a ticket naming host, account and work; not a DC → benign TP; "
        "level 5 → Low.",
        context="Change ticket CHG-2004: adm-frank upgrades the Wazuh agent on lab-srv03 during the Sunday window.",
    ),
    # ------------------------------------------------------------------ audit-log-cleared
    Spec(
        "EV-A013",
        "audit-log-cleared",
        ("60117", 9, "Windows audit log was cleared", ["windows", "logs_cleared"], ["T1070.004"]),
        "lab-ws01",
        "2026-11-11T03:01:12Z",
        win("1102", "lab-ws01", {}, "2026-11-11T03:01:12Z"),
        "The audit log was cleared. Subject: LAB\\alice on lab-ws01.",
        "TP",
        [3],
        ["T1685.005", "T1070.004"],
        [
            "knowledge/playbooks/audit-log-cleared",
            "knowledge/windows-events/event-1102",
            "knowledge/mitre/t1685-005-clear-windows-event-logs",
        ],
        WIN_RULES,
        "Security log cleared at 03:01 by a normal user, no maintenance reason → condition 3 → Critical. "
        "MITRE: handbook page T1685.005; rule table T1070.004 (Q4: both accepted).",
    ),
    Spec(
        "EV-A014",
        "audit-log-cleared",
        ("60117", 9, "Windows audit log was cleared", ["windows", "logs_cleared"], ["T1070.004"]),
        "lab-srv03",
        "2026-11-08T23:40:02Z",
        win("1102", "lab-srv03", {}, "2026-11-08T23:40:02Z"),
        "The audit log was cleared. Subject: LAB\\adm-frank on lab-srv03.",
        "benign_TP",
        [],
        ["T1685.005", "T1070.004"],
        [
            "knowledge/playbooks/audit-log-cleared",
            "knowledge/false-positives/admin-maintenance-windows",
            "knowledge/rules-map/escalation-policy",
        ],
        WIN_RULES,
        "Cleared inside the Sunday window AND the ticket documents the reason → condition 3 ('without a "
        "documented maintenance reason') not met → benign TP; level 9 → Medium.",
        context="Change ticket CHG-2003 documents: archive and clear the Security log on lab-srv03 after disk-full incident, by adm-frank.",
    ),
    # ------------------------------------------------------------------ fim-or-malware-alert
    Spec(
        "EV-A015",
        "fim-or-malware-alert",
        ("554", 5, "File added to the system.", ["ossec", "syscheck", "syscheck_entry_added"], []),
        "lab-srv02",
        "2026-11-11T03:12:40Z",
        {},
        "File '/tmp/.x/kworkerd' added. Mode: realtime. Size: 812344. Owner: deploy.",
        "TP",
        [],
        [],
        [FIM, "knowledge/playbooks/new-local-account"],
        FIM,
        "Hidden directory in /tmp with an executable named like a kernel thread, added minutes after the "
        "backupx account (EV-A010) → TP; level 5 → Low; no condition in this alert.",
        location="syscheck",
        decoder="syscheck_new_entry",
        extra={
            "syscheck": {
                "path": "/tmp/.x/kworkerd",
                "event": "added",
                "size_after": "812344",
                "uname_after": "deploy",
                "sha256_after": "264e9f36917bf1f9bb83390c35bc9865b30bde1f4dc433ac2862bc3d7432e0d1",
            }
        },
    ),
    Spec(
        "EV-A016",
        "fim-or-malware-alert",
        (
            "550",
            7,
            "Integrity checksum changed.",
            ["ossec", "syscheck", "syscheck_entry_modified"],
            ["T1565.001"],
        ),
        "lab-srv04",
        "2026-11-11T14:22:09Z",
        {},
        "File '/etc/passwd' modified. Mode: realtime. Changed attributes: size, mtime, md5, sha256.",
        "needs_info",
        [],
        ["T1565.001"],
        [FIM],
        FIM,
        "/etc/passwd changed outside any patch window; who changed it and why is unknown → needs-info; "
        "level 7 → Medium, so not condition 8.",
        location="syscheck",
        decoder="syscheck_integrity_changed",
        extra={
            "syscheck": {
                "path": "/etc/passwd",
                "event": "modified",
                "changed_attributes": ["size", "mtime", "md5", "sha256"],
            }
        },
    ),
    # ------------------------------------------------------------------ condition 8 (needs-info + High)
    Spec(
        "EV-A019",
        "brute-force",
        (
            "5763",
            10,
            "sshd: brute force trying to get access to the system. Authentication failed.",
            ["syslog", "sshd", "authentication_failures"],
            ["T1110"],
        ),
        "lab-srv04",
        "2026-11-11T11:05:30Z",
        {"srcip": "10.10.20.17", "srcport": "55231", "dstuser": "deploy"},
        "Nov 11 11:05:30 lab-srv04 sshd[4410]: Failed password for deploy from 10.10.20.17 port 55231 ssh2",
        "needs_info",
        [8],
        ["T1110"],
        ["knowledge/playbooks/brute-force", "knowledge/rules-map/escalation-policy", SSH_RULES],
        SSH_RULES,
        "Internal source (lab-ws03) failing as deploy 8+ times: could be a broken script or an intruder; owner "
        "of lab-ws03 unknown → needs-info; level 10 → High → condition 8 → escalate.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    # ================================================================== false-positive pages (2 each)
    Spec(
        "EV-A021",
        "false-positives/admin-maintenance-windows",
        ("67028", 3, "Special privileges assigned to new logon.", ["windows"], ["T1484"]),
        "lab-srv02",
        "2026-11-08T23:10:44Z",
        win(
            "4672",
            "lab-srv02",
            {
                "subjectUserName": "adm-frank",
                "subjectDomainName": "LAB",
                "privilegeList": "SeDebugPrivilege SeTakeOwnershipPrivilege",
            },
            "2026-11-08T23:10:44Z",
        ),
        "Special privileges assigned to new logon: LAB\\adm-frank.",
        "benign_TP",
        [],
        ["T1484"],
        [
            "knowledge/false-positives/admin-maintenance-windows",
            "knowledge/windows-events/event-4672",
        ],
        WIN_RULES,
        "Inside the Sunday window with a ticket naming host, account and work → benign TP; level 3 → Low.",
        context="Change ticket CHG-2002: adm-frank patches lab-srv02 during the Sunday window.",
    ),
    Spec(
        "EV-A022",
        "false-positives/admin-maintenance-windows",
        ("67028", 3, "Special privileges assigned to new logon.", ["windows"], ["T1484"]),
        "lab-srv03",
        "2026-11-08T23:55:02Z",
        win(
            "4672",
            "lab-srv03",
            {
                "subjectUserName": "adm-greg",
                "subjectDomainName": "LAB",
                "privilegeList": "SeDebugPrivilege",
            },
            "2026-11-08T23:55:02Z",
        ),
        "Special privileges assigned to new logon: LAB\\adm-greg.",
        "needs_info",
        [],
        ["T1484"],
        [
            "knowledge/false-positives/admin-maintenance-windows",
            "knowledge/windows-events/event-4672",
        ],
        WIN_RULES,
        "Inside the window but NO change ticket → the window alone proves nothing → needs-info (ask for the "
        "ticket); level 3 → Low.",
        context="No change ticket found for lab-srv03 or adm-greg.",
    ),
    Spec(
        "EV-A023",
        "false-positives/backup-jobs",
        ("67028", 3, "Special privileges assigned to new logon.", ["windows"], ["T1484"]),
        "lab-bkp01",
        "2026-11-11T01:15:09Z",
        win(
            "4672",
            "lab-bkp01",
            {
                "subjectUserName": "svc-backup",
                "subjectDomainName": "LAB",
                "privilegeList": "SeBackupPrivilege SeRestorePrivilege",
            },
            "2026-11-11T01:15:09Z",
        ),
        "Special privileges assigned to new logon: LAB\\svc-backup (SeBackupPrivilege).",
        "benign_TP",
        [],
        ["T1484"],
        [
            "knowledge/false-positives/backup-jobs",
            "knowledge/false-positives/service-accounts",
            "knowledge/windows-events/event-4672",
        ],
        WIN_RULES,
        "SeBackupPrivilege for the listed backup account on its allowed host inside the 01:00–05:00 window → "
        "benign TP; level 3 → Low. NOTE for Naveed: escalation condition 2 lists service accounts, but the "
        "service-accounts/backup pages treat a listed, matching account as benign.",
        context="svc-backup is listed in etc/lists/service-accounts with allowed host lab-bkp01.",
    ),
    Spec(
        "EV-A024",
        "false-positives/backup-jobs",
        (
            "550",
            7,
            "Integrity checksum changed.",
            ["ossec", "syscheck", "syscheck_entry_modified"],
            ["T1565.001"],
        ),
        "lab-bkp01",
        "2026-11-11T02:31:55Z",
        {},
        "File '/srv/backup/catalog/index.db' modified. Changed attributes: size, mtime, sha256.",
        "benign_TP",
        [],
        ["T1565.001"],
        ["knowledge/false-positives/backup-jobs", FIM],
        FIM,
        "Burst of FIM changes in the backup catalog on the backup server inside the backup window by the listed "
        "backup account → benign TP; level 7 → Medium.",
        context="One of 220 FIM changes under /srv/backup between 01:05 and 02:40 UTC, all by svc-backup.",
        location="syscheck",
        decoder="syscheck_integrity_changed",
        extra={
            "syscheck": {
                "path": "/srv/backup/catalog/index.db",
                "event": "modified",
                "uname_after": "svc-backup",
            }
        },
    ),
    Spec(
        "EV-A025",
        "false-positives/expired-or-mistyped-passwords",
        (
            "60122",
            5,
            "Logon Failure - Unknown user or bad password",
            ["windows", "authentication_failed"],
            ["T1531"],
        ),
        "lab-ws02",
        "2026-11-11T08:03:17Z",
        win(
            "4625",
            "lab-ws02",
            {
                "targetUserName": "carol",
                "targetDomainName": "LAB",
                "ipAddress": "-",
                "logonType": "2",
                "status": "0xc000006d",
                "subStatus": "0xc000006a",
                "workstationName": "LAB-WS02",
            },
            "2026-11-11T08:03:17Z",
        ),
        "Interactive logon failure (Type 2, bad password) for LAB\\carol at her workstation.",
        "benign_TP",
        [],
        [],
        [
            "knowledge/false-positives/expired-or-mistyped-passwords",
            "knowledge/windows-events/event-4625",
        ],
        WIN_RULES,
        "2 failures from the user's own workstation, followed by a success, account not privileged → mistyped "
        "password → benign TP (the rule fired correctly on a real, harmless failure); level 5 → Low.",
        context="carol logged on successfully at 08:03:40 UTC; 2 failures in total.",
    ),
    Spec(
        "EV-A026",
        "false-positives/expired-or-mistyped-passwords",
        (
            "60204",
            10,
            "Multiple Windows Logon Failures",
            ["windows", "authentication_failures"],
            ["T1110"],
        ),
        "lab-ws03",
        "2026-11-11T08:30:40Z",
        win(
            "4625",
            "lab-ws03",
            {
                "targetUserName": "henry",
                "targetDomainName": "LAB",
                "ipAddress": "10.10.20.17",
                "logonType": "3",
                "status": "0xc000006d",
                "subStatus": "0xc0000071",
                "workstationName": "LAB-WS03",
            },
            "2026-11-11T08:30:40Z",
        ),
        "9 network logon failures for LAB\\henry from his own workstation, sub-status 0xC0000071 (expired password).",
        "FP",
        [],
        ["T1110"],
        [
            "knowledge/false-positives/expired-or-mistyped-passwords",
            "knowledge/windows-events/event-4625",
            "knowledge/playbooks/brute-force",
        ],
        WIN_RULES,
        "Rule 60204 (brute force) fired, but every failure is 0xC0000071 (expired password) from the user's own "
        "workstation, no success, not privileged → not an attack → FP; level 10 → High; no condition.",
        context="henry's password expired yesterday; his mapped drive keeps retrying with the old password.",
    ),
    Spec(
        "EV-A027",
        "false-positives/service-accounts",
        (
            "67024",
            3,
            "Service logon event registered from non standard service account.",
            ["windows"],
            [],
        ),
        "lab-sql01",
        "2026-11-11T06:00:02Z",
        win(
            "4624",
            "lab-sql01",
            {
                "targetUserName": "svc-sql",
                "targetDomainName": "LAB",
                "logonType": "5",
                "ipAddress": "-",
                "workstationName": "-",
            },
            "2026-11-11T06:00:02Z",
        ),
        "Service logon (Type 5) for LAB\\svc-sql on lab-sql01.",
        "benign_TP",
        [],
        [],
        ["knowledge/false-positives/service-accounts", "knowledge/windows-events/event-4624"],
        WIN_RULES,
        "Listed service account, on its allowed host, Logon Type 5 → benign TP; level 3 → Low.",
        context="svc-sql is listed in etc/lists/service-accounts with allowed host lab-sql01.",
    ),
    Spec(
        "EV-A028",
        "false-positives/service-accounts",
        ("67022", 3, "Non network or service local logon.", ["windows"], []),
        "lab-web01",
        "2026-11-11T04:30:00Z",
        win(
            "4624",
            "lab-web01",
            {
                "targetUserName": "svc-web",
                "targetDomainName": "LAB",
                "logonType": "4",
                "ipAddress": "-",
                "workstationName": "-",
            },
            "2026-11-11T04:30:00Z",
        ),
        "Batch logon (Type 4) for LAB\\svc-web on lab-web01.",
        "benign_TP",
        [],
        [],
        ["knowledge/false-positives/service-accounts", "knowledge/windows-events/event-4624"],
        WIN_RULES,
        "Listed service account, allowed host, Type 4 for the scheduled job named in the list → benign TP; "
        "level 3 → Low.",
        context="svc-web is listed with allowed host lab-web01 and scheduled job 'log-rotate' (Type 4, 04:30 daily).",
    ),
    Spec(
        "EV-A029",
        "false-positives/vulnerability-scanners",
        (
            "5710",
            5,
            "sshd: Attempt to login using a non-existent user",
            ["syslog", "sshd", "authentication_failed"],
            ["T1110.001", "T1021.004"],
        ),
        "lab-srv02",
        "2026-11-10T20:05:13Z",
        {"srcip": "10.10.50.5", "srcport": "41001", "srcuser": "test"},
        "Nov 10 20:05:13 lab-srv02 sshd[1777]: Invalid user test from 10.10.50.5 port 41001",
        "benign_TP",
        [],
        ["T1110.001"],
        [
            "knowledge/false-positives/vulnerability-scanners",
            "knowledge/linux-auth/ssh-invalid-user",
        ],
        SSH_RULES,
        "Source is on the approved-scanners list and inside its recorded weekly schedule → benign TP; level 5 → Low.",
        context="10.10.50.5 is in etc/lists/approved-scanners; recorded schedule: Tuesday 20:00–22:00 UTC weekly.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    Spec(
        "EV-A030",
        "false-positives/vulnerability-scanners",
        (
            "5712",
            10,
            "sshd: brute force trying to get access to the system. Non existent user.",
            ["syslog", "sshd", "authentication_failures"],
            ["T1110"],
        ),
        "lab-web01",
        "2026-11-10T20:41:50Z",
        {"srcip": "10.10.50.5", "srcport": "41877", "srcuser": "admin"},
        "Nov 10 20:41:50 lab-web01 sshd[2002]: Invalid user admin from 10.10.50.5 port 41877",
        "benign_TP",
        [],
        ["T1110"],
        ["knowledge/false-positives/vulnerability-scanners", SSH_RULES],
        SSH_RULES,
        "Brute-force rule fired by the approved scanner inside its schedule, only scanning (no success, no new "
        "service) → benign TP; level 10 → High; no condition.",
        context="10.10.50.5 is in etc/lists/approved-scanners; recorded schedule: Tuesday 20:00–22:00 UTC weekly.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    # ================================================================== ruleset-sourced (INTENT Q2 "haan")
    Spec(
        "EV-A031",
        "port-scan",
        (
            "4151",
            10,
            "Multiple Firewall drop events from same source.",
            ["firewall", "multiple_drops"],
            [],
        ),
        "lab-fw01",
        "2026-11-11T01:47:12Z",
        {
            "srcip": "203.0.113.200",
            "dstip": "10.10.40.10",
            "dstport": "3389",
            "protocol": "TCP",
            "action": "DROP",
        },
        "Nov 11 01:47:12 lab-fw01 kernel: DROP IN=eth0 SRC=203.0.113.200 DST=10.10.40.10 PROTO=TCP DPT=3389",
        "TP",
        [],
        ["T1046"],
        [PORT_SCAN, "knowledge/mitre/t1046-network-service-discovery"],
        RULESET + "0900-firewall_rules.xml#L27",
        "18+ firewall drops in 45 s from one external IP across many ports (rule 4151) → scan → TP; "
        "source not on the approved-scanner list; level 10 → High; no escalation condition.",
        context="The 18 dropped packets hit 18 different TCP ports on lab-web01 within 40 seconds.",
        location="/var/log/kern.log",
        decoder="iptables",
        source_ref="ruleset: 0900-firewall_rules.xml line 27 (rule 4151)",
    ),
    Spec(
        "EV-A032",
        "port-scan",
        ("5731", 6, "sshd: SSH Scanning.", ["syslog", "sshd", "recon"], ["T1046"]),
        "lab-srv02",
        "2026-11-11T02:10:05Z",
        {"srcip": "198.51.100.140", "srcport": "33012"},
        "Nov 11 02:10:05 lab-srv02 sshd[2050]: Did not receive identification string from 198.51.100.140 port 33012",
        "TP",
        [],
        ["T1046"],
        [PORT_SCAN, SSH_RULES, "knowledge/mitre/t1046-network-service-discovery"],
        SSH_RULES,
        "SSH banner probing from an external IP not on the scanner list → reconnaissance → TP; level 6 → Low.",
        location="/var/log/auth.log",
        decoder="sshd",
    ),
    Spec(
        "EV-A033",
        "suspicious-powershell",
        (
            "91809",
            10,
            "Powershell script may be using Base64 decoding method",
            ["windows", "powershell"],
            ["T1140"],
        ),
        "lab-ws02",
        "2026-11-11T03:30:18Z",
        {
            "win": {
                "system": {
                    "eventID": "4104",
                    "computer": "lab-ws02.lab.local",
                    "channel": "Microsoft-Windows-PowerShell/Operational",
                    "providerName": "Microsoft-Windows-PowerShell",
                    "systemTime": "2026-11-11T03:30:18Z",
                },
                "eventdata": {
                    "scriptBlockText": "$s=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('SUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQp')); iex $s",
                    "scriptBlockId": "7d1c2f0e-0000-4000-8000-000000000033",
                    "path": "",
                },
            }
        },
        "Creating Scriptblock text (1 of 1): FromBase64String(...) followed by iex, run by LAB\\alice.",
        "TP",
        [],
        ["T1140", "T1059.001"],
        [PSH, "knowledge/mitre/t1059-001-powershell", "knowledge/sysmon/event-1-process-create"],
        RULESET + "0915-win-powershell_rules.xml#L74",
        "Script block decodes Base64 and pipes it to iex (Invoke-Expression) at 03:30 from a user session → "
        "obfuscated execution → TP; level 10 → High; no escalation condition in this alert.",
        context="The script block ran in a PowerShell session started by WINWORD.EXE (Office) for LAB\\alice.",
        source_ref="ruleset: 0915-win-powershell_rules.xml line 74 (rule 91809)",
    ),
    Spec(
        "EV-A034",
        "suspicious-powershell",
        (
            "91844",
            12,
            "Possible addition of new item to Windows startup registry",
            ["windows", "powershell"],
            ["T1547.001", "T1059.001", "T1112"],
        ),
        "lab-ws02",
        "2026-11-11T03:31:02Z",
        {
            "win": {
                "system": {
                    "eventID": "4104",
                    "computer": "lab-ws02.lab.local",
                    "channel": "Microsoft-Windows-PowerShell/Operational",
                    "providerName": "Microsoft-Windows-PowerShell",
                    "systemTime": "2026-11-11T03:31:02Z",
                },
                "eventdata": {
                    "scriptBlockText": "New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'OneDriveSync' -Value 'C:\\Users\\Public\\odsync.exe'",
                    "scriptBlockId": "7d1c2f0e-0000-4000-8000-000000000034",
                    "path": "",
                },
            }
        },
        "Creating Scriptblock text (1 of 1): New-ItemProperty ... CurrentVersion\\Run ... C:\\Users\\Public\\odsync.exe",
        "TP",
        [1],
        ["T1547.001", "T1059.001", "T1112"],
        [PSH, "knowledge/mitre/t1059-001-powershell", "knowledge/rules-map/escalation-policy"],
        RULESET + "0915-win-powershell_rules.xml#L432",
        "Run-key persistence to an executable in C:\\Users\\Public, 44 s after EV-A033 on the same host → TP; "
        "rule level 12 → escalation condition 1 → Critical.",
        source_ref="ruleset: 0915-win-powershell_rules.xml line 432 (rule 91844)",
    ),
    # ================================================================== OTRF-mapped (INTENT Q1 "haan")
    Spec(
        "EV-A035",
        "new-service-or-scheduled-task",
        (
            "92068",
            3,
            'PSEXEC was used to execute: "reg" save HKLM\\security\\policy\\secrets',
            ["sysmon", "sysmon_event1"],
            ["T1569.002"],
        ),
        "WORKSTATION5",
        "2020-10-19T07:30:46.660Z",
        {
            "win": {
                "system": {
                    "eventID": "1",
                    "computer": "WORKSTATION5",
                    "channel": "Microsoft-Windows-Sysmon/Operational",
                    "providerName": "Microsoft-Windows-Sysmon",
                    "systemTime": "2020-10-19T07:30:46.660Z",
                },
                "eventdata": {
                    "image": "C:\\Windows\\System32\\reg.exe",
                    "commandLine": '"reg" save HKLM\\security\\policy\\secrets C:\\Users\\wardog\\AppData\\Local\\Temp\\secrets',
                    "parentImage": "C:\\Windows\\PSEXESVC.exe",
                    "parentCommandLine": "C:\\windows\\PSEXESVC.exe",
                    "user": "NT AUTHORITY\\SYSTEM",
                },
            }
        },
        "Process Create: reg.exe save HKLM\\security\\policy\\secrets, parent PSEXESVC.exe, user NT AUTHORITY\\SYSTEM.",
        "TP",
        [],
        ["T1569.002"],
        [
            "knowledge/playbooks/new-service-or-scheduled-task",
            "knowledge/sysmon/event-1-process-create",
        ],
        RULESET + "0800-sysmon_id_1.xml#L734",
        "PsExec service runs reg.exe to save the LSA secrets hive → credential theft via remote execution → TP. "
        "Rule level 3 → Low by the severity model, no escalation condition. NOTE for Naveed: the policy gives "
        "credential theft no condition of its own.",
        source="OTRF",
        source_ref=OTRF
        + "credential_access/host/cmd_psexec_lsa_secrets_dump.zip (Sysmon 1, UtcTime 2020-10-19 07:30:46.660)",
    ),
    Spec(
        "EV-A036",
        "new-service-or-scheduled-task",
        ("61138", 5, "New Windows Service Created", ["windows", "windows_system"], ["T1543.003"]),
        "WORKSTATION5",
        "2020-10-19T07:30:46.416Z",
        win(
            "7045",
            "WORKSTATION5",
            {
                "serviceName": "PSEXESVC",
                "imagePath": "%SystemRoot%\\PSEXESVC.exe",
                "serviceType": "user mode service",
                "startType": "demand start",
                "accountName": "LocalSystem",
            },
            "2020-10-19T07:30:46.416Z",
        ),
        "A service was installed: PSEXESVC, %SystemRoot%\\PSEXESVC.exe, demand start, LocalSystem.",
        "TP",
        [],
        ["T1543.003"],
        [
            "knowledge/playbooks/new-service-or-scheduled-task",
            "knowledge/windows-events/event-7045",
        ],
        WIN_RULES,
        "PSEXESVC installed; the same session then dumps LSA secrets (EV-A035) → TP; not a DC → no condition 7; "
        "level 5 → Low.",
        context="No admin work was scheduled on WORKSTATION5; 0.3 s later PSEXESVC started reg.exe (alert EV-A035).",
        source="OTRF",
        source_ref=OTRF + "credential_access/host/cmd_psexec_lsa_secrets_dump.zip (System 7045)",
    ),
    Spec(
        "EV-A037",
        "success-after-failures",
        ("60106", 3, "Windows Logon Success", ["windows", "authentication_success"], ["T1078"]),
        "WORKSTATION6",
        "2020-08-06T06:27:10.554Z",
        win(
            "4624",
            "WORKSTATION6",
            {
                "targetUserName": "pgustavo",
                "targetDomainName": "THESHIRE.LOCAL",
                "logonType": "3",
                "ipAddress": "172.18.39.5",
                "workstationName": "-",
            },
            "2020-08-06T06:27:10.554Z",
        ),
        "Network logon (Type 3) for THESHIRE\\pgustavo on WORKSTATION6 from 172.18.39.5.",
        "needs_info",
        [],
        ["T1078"],
        ["knowledge/windows-events/event-4624", "knowledge/wazuh/asset-and-user-context"],
        WIN_RULES,
        "A single network logon; whether pgustavo normally connects to WORKSTATION6 from 172.18.39.5 is unknown "
        "→ needs-info; level 3 → Low.",
        source="OTRF",
        source_ref=OTRF
        + "lateral_movement/host/covenant_sharpsc_create_dcerpc_smb_svcctl.zip (Security 4624)",
    ),
    Spec(
        "EV-A038",
        "lateral-movement (no playbook)",
        ("67028", 3, "Special privileges assigned to new logon.", ["windows"], ["T1484"]),
        "WORKSTATION6",
        "2020-08-06T06:27:10.554Z",
        win(
            "4672",
            "WORKSTATION6",
            {
                "subjectUserName": "pgustavo",
                "subjectDomainName": "THESHIRE",
                "privilegeList": "SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege SeTakeOwnershipPrivilege SeDebugPrivilege SeSystemEnvironmentPrivilege SeLoadDriverPrivilege SeImpersonatePrivilege SeDelegateSessionUserImpersonatePrivilege",
            },
            "2020-08-06T06:27:10.554Z",
        ),
        "Special privileges assigned to new logon: THESHIRE\\pgustavo (SeDebugPrivilege, SeLoadDriverPrivilege, ...).",
        "needs_info",
        [2, 8],
        ["T1484"],
        ["knowledge/windows-events/event-4672", "knowledge/rules-map/escalation-policy"],
        WIN_RULES,
        "Admin-level privileges at a network logon (with EV-A037): pgustavo acts as a privileged account → "
        "condition 2 → High; whether this admin logon is expected is unknown → needs-info (High → also condition 8).",
        source="OTRF",
        source_ref=OTRF
        + "lateral_movement/host/covenant_sharpsc_create_dcerpc_smb_svcctl.zip (Security 4672)",
    ),
    Spec(
        "EV-A039",
        "new-service-or-scheduled-task",
        ("61138", 5, "New Windows Service Created", ["windows", "windows_system"], ["T1543.003"]),
        "WORKSTATION6",
        "2020-08-06T06:27:31.787Z",
        win(
            "7045",
            "WORKSTATION6",
            {
                "serviceName": "OTR",
                "imagePath": "C:\\Windows\\System32\\GruntHTTP2.exe",
                "serviceType": "user mode service",
                "startType": "auto start",
                "accountName": "pgustavo",
            },
            "2020-08-06T06:27:31.787Z",
        ),
        "A service was installed: OTR, C:\\Windows\\System32\\GruntHTTP2.exe, auto start, run as pgustavo.",
        "TP",
        [],
        ["T1543.003"],
        [
            "knowledge/playbooks/new-service-or-scheduled-task",
            "knowledge/windows-events/event-7045",
            "knowledge/mitre/t1543-003-windows-service",
        ],
        WIN_RULES,
        "Remote service creation 21 s after a network logon, unusual image name in System32, auto start → TP "
        "(remote service persistence); not a DC → no condition 7; level 5 → Low.",
        context="Created 21 seconds after the Type 3 logon of pgustavo from 172.18.39.5 (alert EV-A037).",
        source="OTRF",
        source_ref=OTRF
        + "lateral_movement/host/covenant_sharpsc_create_dcerpc_smb_svcctl.zip (System 7045)",
    ),
    Spec(
        "EV-A040",
        "fim-or-malware-alert",
        ("554", 5, "File added to the system.", ["ossec", "syscheck", "syscheck_entry_added"], []),
        "WORKSTATION5",
        "2020-10-19T07:30:47.120Z",
        {},
        "File 'c:\\users\\wardog\\appdata\\local\\temp\\secrets' added. Mode: realtime.",
        "TP",
        [],
        [],
        [FIM, "knowledge/playbooks/new-service-or-scheduled-task"],
        FIM,
        "The saved LSA-secrets hive file written by reg.exe under PsExec (EV-A035) → TP; level 5 → Low. "
        "NOTE: FIM on this temp path assumes a lab FIM config; OTRF records the file write (Sysmon 11).",
        location="syscheck",
        decoder="syscheck_new_entry",
        extra={
            "syscheck": {
                "path": "c:\\users\\wardog\\appdata\\local\\temp\\secrets",
                "event": "added",
                "uname_after": "SYSTEM",
            }
        },
        source="OTRF",
        source_ref=OTRF
        + "credential_access/host/cmd_psexec_lsa_secrets_dump.zip (Sysmon 11 file create, mapped to FIM 554)",
    ),
]


def to_alert(s: Spec) -> dict[str, Any]:
    rid, level, desc, groups, mitre = s.rule
    alert: dict[str, Any] = {
        "id": s.aid,
        "timestamp": s.ts,
        "rule": {
            "id": rid,
            "level": level,
            "description": desc,
            "groups": groups,
            "mitre": {"id": mitre},
        },
        "agent": {
            "id": AGENT_IDS[s.host],
            "name": s.host,
            **({"ip": HOSTS[s.host]} if HOSTS[s.host] else {}),
        },
        "manager": {"name": "lab-wazuh"},
        "decoder": {"name": s.decoder},
        "location": s.location,
        "data": {k: v for k, v in s.data.items() if v is not None},
        "full_log": s.full_log,
    }
    alert.update(s.extra)
    if s.aid == "EV-A013":
        alert["data"]["win"]["logFileCleared"] = {
            "subjectUserName": "alice",
            "subjectDomainName": "LAB",
        }
    if s.aid == "EV-A014":
        alert["data"]["win"]["logFileCleared"] = {
            "subjectUserName": "adm-frank",
            "subjectDomainName": "LAB",
        }
    if not alert["data"]:
        del alert["data"]
    return alert


def main() -> None:
    (DATA / "alerts").mkdir(parents=True, exist_ok=True)
    labels, contexts = [], []
    for s in sorted(SPECS, key=lambda x: x.aid):
        path = DATA / "alerts" / f"{s.aid}.json"
        path.write_text(
            json.dumps(to_alert(s), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        labels.append(
            {
                "alert_id": s.aid,
                "source": s.source,
                "source_ref": s.source_ref
                or f"synthetic: built from {s.rule_source} + {s.pages[0]}",
                "playbook": s.playbook,
                "verdict": s.verdict,
                "severity": severity(s.rule[1], s.conditions, s.host),
                "escalate": "yes" if s.conditions else "no",
                "escalate_condition": str(s.conditions[0]) if s.conditions else "",
                "also_conditions": ";".join(str(c) for c in s.conditions[1:]),
                "mitre_ids": ";".join(s.mitre),
                "expected_stable_ids": ";".join(s.pages),
                "rule_source": s.rule_source,
                "rationale": s.rationale,
                "verified_by": "",
                "verified_at": "",
            }
        )
        if s.context:
            contexts.append({"alert_id": s.aid, "analyst_context": s.context})
    for name, rows in (("labels.csv", labels), ("context.csv", contexts)):
        with (DATA / name).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(f"wrote {len(labels)} alerts, {len(contexts)} contexts")


if __name__ == "__main__":
    main()

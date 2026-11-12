"""Compiled patterns used by the masking engine (FR-01-32).

Regexes only FIND candidates. For IPs, the standard-library `ipaddress` parser decides
whether a candidate is really an address, so times (12:30:45), MAC addresses and version
strings are not masked.
"""

import re

TOKEN_RE = re.compile(r"<(?:IP|USER|HOST|EMAIL)-\d+>")

EMAIL_RE = re.compile(
    r"(?<![\w.%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![\w-])"
)

# DOMAIN\user — DOMAIN is a NetBIOS-style upper-case name, so "Program Files\Microsoft" or
# "C:\Windows\System32" (paths) do not match; the user part must not continue as a path.
DOMAIN_USER_RE = re.compile(
    r"(?<![\w\\/:.-])(?P<domain>[A-Z0-9][A-Z0-9-]{0,14})\\(?P<user>[A-Za-z0-9._$-]{1,64})(?![\w\\$.-])"
)

IPV6_CANDIDATE_RE = re.compile(
    r"(?<![\w:.])(?:[0-9A-Fa-f]{0,4}:){2,7}(?:(?:\d{1,3}\.){3}\d{1,3}|[0-9A-Fa-f]{0,4})(?![\w:])"
)

# A trailing "." is allowed (end of sentence) but not ".<digit>" (longer dotted number)
# and not "/<digit>" (a CIDR range is not one host).
IPV4_CANDIDATE_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?!\w|\.\d|/\d)")

INTERNAL_SUFFIXES: tuple[str, ...] = ("local", "lan", "corp", "internal", "intra", "home.arpa")


def internal_fqdn_re(suffixes: tuple[str, ...] = INTERNAL_SUFFIXES) -> re.Pattern[str]:
    alt = "|".join(re.escape(s) for s in suffixes)
    return re.compile(
        r"(?<![\w.-])(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?:" + alt + r")(?![\w-])",
        re.IGNORECASE,
    )


# Built-in principals kept unmasked: they are not personal data, and triage needs them
# (e.g. escalation condition 2 — a privileged account is the target).
WELL_KNOWN_PRINCIPALS = frozenset(
    s.casefold()
    for s in (
        "SYSTEM",
        "LOCAL SERVICE",
        "NETWORK SERVICE",
        "ANONYMOUS LOGON",
        "Administrator",
        "Guest",
        "DefaultAccount",
        "krbtgt",
        "root",
        # Built-in groups (4728/4732/4756 put the GROUP name in targetUserName). Condition 6
        # ("added to Administrators") cannot be seen if these are masked.
        "Administrators",
        "Domain Admins",
        "Enterprise Admins",
        "Schema Admins",
        "Backup Operators",
        "Remote Desktop Users",
        "Users",
        "-",
        "",
    )
)

# Keys whose values are secrets: the whole field is dropped from the masked alert.
# File hashes (e.g. Sysmon "hashes") are IOCs and are kept (INTENT Q1).
SECRET_KEY_RE = re.compile(
    r"(?i)^(?:.*pass(?:word|wd)?.*|pwd|.*secret.*|api_?key|.*(?:access|auth|refresh|bearer)_?token"
    r"|.*(?:ntlm|lm)_?hash)$"
)

"""FR-01-30…32, 36…38 and spec §4 edge cases — free-text masking."""

import pytest
from soc_shared.masking import (
    Kind,
    MaskMap,
    find_leaks,
    find_unmasked_pii,
    mask_text,
    unmask,
)


@pytest.fixture
def m() -> MaskMap:
    return MaskMap()


class TestMaskMap:
    def test_tokens_numbered_per_kind(self, m: MaskMap) -> None:
        assert m.token_for(Kind.IP, "10.0.0.5") == "<IP-1>"
        assert m.token_for(Kind.IP, "10.0.0.6") == "<IP-2>"
        assert m.token_for(Kind.USER, "alice") == "<USER-1>"
        assert m.token_for(Kind.HOST, "lab-ws01") == "<HOST-1>"
        assert m.token_for(Kind.EMAIL, "a@lab.example") == "<EMAIL-1>"

    def test_same_value_same_token(self, m: MaskMap) -> None:
        assert m.token_for(Kind.IP, "10.0.0.5") == m.token_for(Kind.IP, " 10.0.0.5 ")
        assert m.token_for(Kind.USER, "Admin1") == m.token_for(Kind.USER, "admin1")
        assert m.token_for(Kind.HOST, "LAB-WS01") == m.token_for(Kind.HOST, "lab-ws01")
        assert m.token_for(Kind.EMAIL, "Bob@Lab.Example") == m.token_for(
            Kind.EMAIL, "bob@lab.example"
        )

    def test_ipv6_normalised(self, m: MaskMap) -> None:
        assert m.token_for(Kind.IP, "2001:DB8:0:0:0:0:0:1") == m.token_for(Kind.IP, "2001:db8::1")

    def test_repr_has_no_values(self, m: MaskMap) -> None:
        m.token_for(Kind.IP, "10.0.0.5")
        m.token_for(Kind.USER, "alice")
        assert repr(m) == "MaskMap(IP=1, USER=1, HOST=0, EMAIL=0)"
        assert "10.0.0.5" not in str(m)

    def test_storage_entries_hide_value_in_repr(self, m: MaskMap) -> None:
        m.token_for(Kind.USER, "alice")
        (entry,) = m.to_storage()
        assert (entry.token, entry.kind, entry.value) == ("<USER-1>", Kind.USER, "alice")
        assert "alice" not in repr(entry)

    def test_lookup_helpers(self, m: MaskMap) -> None:
        tok = m.token_for(Kind.HOST, "lab-ws01")
        assert m.get_token(Kind.HOST, "LAB-WS01") == tok
        assert m.get_token(Kind.HOST, "other") is None
        assert m.value_of(tok) == "lab-ws01"
        assert m.kind_of(tok) is Kind.HOST
        assert tok in m and "<HOST-9>" not in m
        assert len(m) == 1


class TestMaskText:
    def test_ipv4_same_value_same_token(self, m: MaskMap) -> None:
        out = mask_text("Login from 10.0.0.5 and again 10.0.0.5, then 10.0.0.6.", m)
        assert out == "Login from <IP-1> and again <IP-1>, then <IP-2>."

    def test_ipv4_with_port_keeps_port(self, m: MaskMap) -> None:
        assert mask_text("conn 203.0.113.5:443", m) == "conn <IP-1>:443"

    def test_ip_in_url(self, m: MaskMap) -> None:
        assert mask_text("iwr http://203.0.113.80/a.ps1", m) == "iwr http://<IP-1>/a.ps1"

    def test_cidr_is_not_a_host(self, m: MaskMap) -> None:
        assert mask_text("range 10.0.0.0/8 is private", m) == "range 10.0.0.0/8 is private"

    @pytest.mark.parametrize("text", ["999.1.1.1", "version 10.0.19041.1", "v1.2.3.4", "1.2.3.4.5"])
    def test_not_an_ipv4(self, m: MaskMap, text: str) -> None:
        assert mask_text(text, m) == text

    def test_ipv6(self, m: MaskMap) -> None:
        assert mask_text("from 2001:db8::1 and fe80::1%eth0 x", m).startswith(
            "from <IP-1> and <IP-2>"
        )

    def test_ipv4_mapped_ipv6_same_token_as_ipv4(self, m: MaskMap) -> None:
        assert mask_text("a 10.0.0.5 b ::ffff:10.0.0.5", m) == "a <IP-1> b <IP-1>"

    @pytest.mark.parametrize(
        "text", ["at 12:30:45", "mac 00:1A:2B:3C:4D:5E", "std::vector", "x::y"]
    )
    def test_not_an_ipv6(self, m: MaskMap, text: str) -> None:
        assert mask_text(text, m) == text

    def test_email(self, m: MaskMap) -> None:
        assert mask_text("mail alice@lab.example now", m) == "mail <EMAIL-1> now"

    def test_upn_in_free_text_is_email(self, m: MaskMap) -> None:
        assert mask_text("user alice@lab.local logged on", m) == "user <EMAIL-1> logged on"

    def test_domain_user(self, m: MaskMap) -> None:
        assert mask_text(r"by LAB\alice ok", m) == r"by <HOST-1>\<USER-1> ok"
        assert m.value_of("<USER-1>") == "alice"

    def test_machine_account_is_host(self, m: MaskMap) -> None:
        assert mask_text(r"LAB\LAB-WS01$ logged on", m) == r"<HOST-1>\<HOST-2>$ logged on"

    @pytest.mark.parametrize(
        "text",
        [
            r"C:\Windows\System32\cmd.exe",
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"HKLM\SOFTWARE\Microsoft\Windows\Run",
            r"NT AUTHORITY\SYSTEM",
        ],
    )
    def test_paths_and_well_known_principals_unchanged(self, m: MaskMap, text: str) -> None:
        assert mask_text(text, m) == text

    def test_internal_fqdn(self, m: MaskMap) -> None:
        assert mask_text("to lab-ws01.lab.local now", m) == "to <HOST-1> now"
        assert mask_text("dc01.corp", m) == "<HOST-2>"

    def test_public_domains_unchanged(self, m: MaskMap) -> None:
        text = "see https://attack.mitre.org/techniques/T1110/ and learn.microsoft.com"
        assert mask_text(text, m) == text

    def test_learned_host_and_user_masked_everywhere(self, m: MaskMap) -> None:
        m.token_for(Kind.HOST, "lab-srv02")
        m.token_for(Kind.USER, "alice")
        out = mask_text("Nov 12 lab-srv02 sshd: Failed password for alice; LAB-SRV02 again", m)
        assert out == "Nov 12 <HOST-1> sshd: Failed password for <USER-1>; <HOST-1> again"

    def test_learned_names_respect_word_boundaries(self, m: MaskMap) -> None:
        m.token_for(Kind.USER, "ali")
        assert mask_text("malice alias ali", m) == "malice alias <USER-1>"

    def test_short_learned_names_not_searched(self, m: MaskMap) -> None:
        m.token_for(Kind.USER, "al")
        assert mask_text("al is short", m) == "al is short"

    def test_idempotent(self, m: MaskMap) -> None:
        once = mask_text(r"LAB\alice from 10.0.0.5 mail a@lab.example", m)
        assert mask_text(once, m) == once

    def test_existing_tokens_never_remasked(self, m: MaskMap) -> None:
        assert mask_text("<IP-7> and <USER-3>", m) == "<IP-7> and <USER-3>"


class TestUnmaskAndChecks:
    def test_round_trip(self, m: MaskMap) -> None:
        text = r"LAB\alice from 10.0.0.5 to lab-ws01.lab.local, mail bob@lab.example"
        assert unmask(mask_text(text, m), m) == text

    def test_unknown_token_left(self, m: MaskMap) -> None:
        assert unmask("<IP-99> stays", m) == "<IP-99> stays"

    def test_find_leaks_returns_tokens_only(self, m: MaskMap) -> None:
        masked = mask_text("from 10.0.0.5 by LAB\\alice", m)
        assert find_leaks(masked, m) == []
        leaks = find_leaks("model said alice used 10.0.0.5", m)
        assert set(leaks) == {"<IP-1>", "<USER-1>"}
        assert "alice" not in leaks

    def test_find_unmasked_pii(self) -> None:
        assert find_unmasked_pii("<IP-1> and <EMAIL-2>") == []
        hits = find_unmasked_pii("x 8.8.8.8 y a@b.example z 2001:db8::1 w 12:30:45")
        assert sorted(hits) == sorted(["8.8.8.8", "a@b.example", "2001:db8::1"])

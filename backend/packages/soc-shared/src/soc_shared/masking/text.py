"""Free-text masking and checks (FR-01-32, 36, 37)."""

import re
from collections.abc import Callable

from soc_shared.masking.ipclass import parse_ip
from soc_shared.masking.maskmap import Kind, MaskMap
from soc_shared.masking.patterns import (
    DOMAIN_USER_RE,
    EMAIL_RE,
    INTERNAL_SUFFIXES,
    IPV4_CANDIDATE_RE,
    IPV6_CANDIDATE_RE,
    TOKEN_RE,
    WELL_KNOWN_PRINCIPALS,
    internal_fqdn_re,
)

# A learned name shorter than this is not searched for in free text (it would hit
# ordinary words); it is still masked in its own field.
MIN_FREE_TEXT_LEN = 3


def _outside_tokens(text: str, fn: Callable[[str], str]) -> str:
    """Apply `fn` to every part of `text` that is not already a token (idempotence)."""
    parts = TOKEN_RE.split(text)
    found = TOKEN_RE.findall(text)
    out = [fn(parts[0])]
    for tok, part in zip(found, parts[1:], strict=True):
        out.append(tok)
        out.append(fn(part))
    return "".join(out)


def mask_domain_user(domain: str, user: str, mask_map: MaskMap) -> str:
    if user.casefold() in WELL_KNOWN_PRINCIPALS:
        return f"{domain}\\{user}"
    domain_tok = mask_map.token_for(Kind.HOST, domain)  # a NetBIOS domain can name the org
    if user.endswith("$"):  # computer account → a host
        user_tok = mask_map.token_for(Kind.HOST, user[:-1]) + "$"
    else:
        user_tok = mask_map.token_for(Kind.USER, user)
    return f"{domain_tok}\\{user_tok}"


def _known_values_re(mask_map: MaskMap, kind: Kind) -> re.Pattern[str] | None:
    values = sorted(
        {v for v, _ in mask_map.known_values(kind) if len(v) >= MIN_FREE_TEXT_LEN},
        key=len,
        reverse=True,
    )
    if not values:
        return None
    alt = "|".join(re.escape(v) for v in values)
    return re.compile(r"(?<![\w.-])(?:" + alt + r")(?![\w-]|\.\w)", re.IGNORECASE)


def mask_text(
    text: str, mask_map: MaskMap, internal_suffixes: tuple[str, ...] = INTERNAL_SUFFIXES
) -> str:
    """Replace emails, DOMAIN\\user, IPv6, IPv4, internal FQDNs and learned names with tokens."""

    def emails(s: str) -> str:
        return EMAIL_RE.sub(lambda m: mask_map.token_for(Kind.EMAIL, m.group()), s)

    def domain_users(s: str) -> str:
        return DOMAIN_USER_RE.sub(lambda m: mask_domain_user(m["domain"], m["user"], mask_map), s)

    def ips(pattern: re.Pattern[str]) -> Callable[[str], str]:
        def sub(s: str) -> str:
            def repl(m: re.Match[str]) -> str:
                return mask_map.token_for(Kind.IP, m.group()) if parse_ip(m.group()) else m.group()

            return pattern.sub(repl, s)

        return sub

    fqdn_re = internal_fqdn_re(internal_suffixes)

    def fqdns(s: str) -> str:
        return fqdn_re.sub(lambda m: mask_map.token_for(Kind.HOST, m.group()), s)

    def learned(kind: Kind) -> Callable[[str], str]:
        # Built when the step starts (so names learned by earlier steps are included),
        # then reused for every text segment of this step.
        pattern = _known_values_re(mask_map, kind)
        if pattern is None:
            return lambda s: s
        return lambda s: pattern.sub(lambda m: mask_map.token_for(kind, m.group()), s)

    # IPv6 runs before IPv4 so "::ffff:10.0.0.5" becomes one token (the same one as 10.0.0.5).
    steps: list[Callable[[], Callable[[str], str]]] = [
        lambda: emails,
        lambda: domain_users,
        lambda: ips(IPV6_CANDIDATE_RE),
        lambda: ips(IPV4_CANDIDATE_RE),
        lambda: fqdns,
        lambda: learned(Kind.HOST),
        lambda: learned(Kind.USER),
    ]
    for make_step in steps:
        text = _outside_tokens(text, make_step())
    return text


def unmask(text: str, mask_map: MaskMap) -> str:
    """Put the real values back (api-gateway only, for the human). Unknown tokens stay."""
    return TOKEN_RE.sub(lambda m: mask_map.value_of(m.group()) or m.group(), text)


def find_leaks(text: str, mask_map: MaskMap) -> list[str]:
    """TOKENS whose raw value appears in `text`. Safe to log: no raw value is returned."""
    leaks: list[str] = []
    stripped = TOKEN_RE.sub(" ", text)
    for token in mask_map.tokens():
        value = mask_map.value_of(token) or ""
        if len(value) < MIN_FREE_TEXT_LEN and mask_map.kind_of(token) is not Kind.IP:
            continue
        pattern = r"(?<![\w.-])" + re.escape(value) + r"(?![\w-]|\.\w)"
        if re.search(pattern, stripped, re.IGNORECASE):
            leaks.append(token)
    return leaks


def find_unmasked_pii(text: str) -> list[str]:
    """IP addresses and emails in `text` that are not tokens. Do NOT log the result."""
    stripped = TOKEN_RE.sub(" ", text)
    hits = [m.group() for m in EMAIL_RE.finditer(stripped)]
    for pattern in (IPV6_CANDIDATE_RE, IPV4_CANDIDATE_RE):
        hits += [m.group() for m in pattern.finditer(stripped) if parse_ip(m.group())]
    return hits

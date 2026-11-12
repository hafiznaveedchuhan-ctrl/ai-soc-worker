"""Masking engine: replace IPs, usernames, hostnames and emails with tokens before any LLM,
web, log or trace call (constitution Art. III; handbook rules-map/data-handling)."""

from soc_shared.masking.alert import mask_alert
from soc_shared.masking.ipclass import classify_ip, is_public_ip, parse_ip
from soc_shared.masking.maskmap import Kind, MaskEntry, MaskMap
from soc_shared.masking.text import find_leaks, find_unmasked_pii, mask_text, unmask

__all__ = [
    "Kind",
    "MaskEntry",
    "MaskMap",
    "classify_ip",
    "find_leaks",
    "find_unmasked_pii",
    "is_public_ip",
    "mask_alert",
    "mask_text",
    "parse_ip",
    "unmask",
]

"""Handbook bands for an AbuseIPDB score (knowledge/enrichment/ip-reputation-policy)."""

from typing import Literal

Band = Literal["none", "low", "suspicious", "likely_malicious"]


def band(score: int) -> Band:
    if score <= 0:
        return "none"  # "No AbuseIPDB reports (not proof of safety)"
    if score <= 24:
        return "low"
    if score <= 74:
        return "suspicious"
    return "likely_malicious"  # 75–100: raises severity one step (applied by the agent, not here)

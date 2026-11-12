"""AbuseIPDB v2 CHECK client (docs.abuseipdb.com, checked in Context7 2026-11-12).

GET {base}/check?ipAddress=<ip>&maxAgeInDays=<n> with headers Key and Accept: application/json.
The response is validated; any surprise becomes an error result, never a crash.
"""

from datetime import datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CheckData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ipAddress: str
    isPublic: bool | None = None
    abuseConfidenceScore: int = Field(ge=0, le=100)
    totalReports: int = Field(default=0, ge=0)
    numDistinctUsers: int = Field(default=0, ge=0)
    countryCode: str | None = None
    usageType: str | None = None
    lastReportedAt: datetime | None = None


class CheckResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: CheckData


class AbuseIpdbError(Exception):
    def __init__(self, reason: str, retry_after: int | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.retry_after = retry_after


class AbuseIpdbClient:
    def __init__(
        self, http: httpx.AsyncClient, base_url: str, api_key: str, max_age_days: int
    ) -> None:
        self._http = http
        self._base = base_url.rstrip("/")
        self._key = api_key
        self._max_age = max_age_days

    async def check(self, ip: str) -> CheckData:
        try:
            resp = await self._http.get(
                f"{self._base}/check",
                params={"ipAddress": ip, "maxAgeInDays": str(self._max_age)},
                headers={"Key": self._key, "Accept": "application/json"},
            )
        except httpx.TimeoutException as exc:
            raise AbuseIpdbError("timeout") from exc
        except httpx.HTTPError as exc:
            raise AbuseIpdbError("network error") from exc
        if resp.status_code == 429:
            retry = resp.headers.get("Retry-After")
            raise AbuseIpdbError("rate limited", int(retry) if retry and retry.isdigit() else None)
        if resp.status_code in (401, 403):
            raise AbuseIpdbError("key rejected by AbuseIPDB")
        if resp.status_code != 200:
            raise AbuseIpdbError(f"http {resp.status_code}")
        try:
            return CheckResponse.model_validate_json(resp.content).data
        except ValidationError as exc:
            raise AbuseIpdbError("unexpected response schema") from exc

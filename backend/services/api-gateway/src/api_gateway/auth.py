"""Authentication (Auth0 JWT via JWKS, ADR-0005) and roles (analyst / admin).

DEV mode (`AUTH_MODE=dev`, never with ENV=production): header `X-Dev-User: <id>[:role]`
for terminal tests.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import jwt
from fastapi import HTTPException

ROLES = ("analyst", "admin")


@dataclass(frozen=True)
class Principal:
    sub: str
    email: str | None
    role: str


class JwksClient(Protocol):
    def get_signing_key_from_jwt(self, token: str | bytes) -> Any: ...


class Authenticator:
    def __init__(
        self, mode: str, domain: str, audience: str, role_claim: str, jwks: JwksClient | None = None
    ) -> None:
        self.mode = mode
        self.issuer = f"https://{domain}/" if domain else ""
        self.audience = audience
        self.role_claim = role_claim
        if mode == "auth0" and jwks is None:
            jwks = jwt.PyJWKClient(f"https://{domain}/.well-known/jwks.json", cache_keys=True)
        self._jwks = jwks

    def authenticate(self, authorization: str | None, dev_user: str | None) -> Principal:
        if self.mode == "dev":
            if not dev_user:
                raise HTTPException(401, "dev mode: send X-Dev-User: <id>[:analyst|admin]")
            sub, _, role = dev_user.partition(":")
            return Principal(
                sub=f"dev|{sub}", email=None, role=role if role in ROLES else "analyst"
            )
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(401, "missing bearer token", headers={"WWW-Authenticate": "Bearer"})
        token = authorization.split(" ", 1)[1]
        if self._jwks is None:
            raise HTTPException(500, "JWKS client not configured")
        try:
            key = self._jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(
                401, f"invalid token: {type(exc).__name__}", headers={"WWW-Authenticate": "Bearer"}
            ) from exc
        roles = claims.get(self.role_claim) or []
        role = "admin" if "admin" in roles else "analyst" if "analyst" in roles else ""
        if not role:
            raise HTTPException(403, "no soc-worker role assigned")
        return Principal(sub=str(claims["sub"]), email=claims.get("email"), role=role)

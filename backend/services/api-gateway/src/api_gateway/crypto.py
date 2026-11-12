"""Fernet encryption of mask-map values (ADR-0007). Key: MASK_MAP_KEY (url-safe base64)."""

from cryptography.fernet import Fernet, InvalidToken


class MaskVault:
    def __init__(self, key: str) -> None:
        self._f = Fernet(key.encode())

    def seal(self, value: str) -> str:
        return self._f.encrypt(value.encode()).decode()

    def open(self, token: str) -> str | None:
        try:
            return self._f.decrypt(token.encode()).decode()
        except InvalidToken:
            return None

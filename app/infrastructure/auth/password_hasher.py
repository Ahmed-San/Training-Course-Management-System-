from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from app.domain.exceptions import AuthenticationError

_ALGORITHM = "sha256"
_ITERATIONS = 600_000
_SALT_BYTES = 16


class PasswordHasher:
    """Small standard-library password hashing adapter for the demo system."""

    def hash(self, password: str) -> str:
        if not isinstance(password, str) or not password:
            raise AuthenticationError("Password must not be empty.")
        salt = secrets.token_bytes(_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            _ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS
        )
        return (
            f"pbkdf2_{_ALGORITHM}${_ITERATIONS}$"
            f"{_encode(salt)}${_encode(digest)}"
        )

    def verify(self, password: str, stored_hash: str) -> bool:
        try:
            scheme, iterations, salt_text, digest_text = stored_hash.split("$", maxsplit=3)
            if scheme != f"pbkdf2_{_ALGORITHM}":
                return False
            salt = _decode(salt_text)
            expected = _decode(digest_text)
            actual = hashlib.pbkdf2_hmac(
                _ALGORITHM,
                password.encode("utf-8"),
                salt,
                int(iterations),
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))

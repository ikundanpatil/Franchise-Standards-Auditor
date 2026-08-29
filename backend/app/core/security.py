"""
Password hashing and JWT issue/verify.

Kept deliberately small and framework-agnostic: FastAPI wiring lives in
``app.api.deps``; this module only knows about strings, times and claims.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from app.core.config import settings

TokenType = Literal["access", "refresh"]

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Passwords ----------------------------------------------------------------
def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except ValueError:
        # Malformed hash in the DB — treat as a non-match rather than a 500.
        return False


def needs_rehash(hashed: str) -> bool:
    return _pwd_context.needs_update(hashed)


# --- JWT ----------------------------------------------------------------
def _now() -> datetime:
    return datetime.now(tz=UTC)


def create_token(
    subject: str | uuid.UUID,
    *,
    token_type: TokenType,
    role: str | None = None,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Return a signed JWT for ``subject`` (typically a user id)."""
    if expires_delta is None:
        minutes = (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
            if token_type == "access"
            else settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        expires_delta = timedelta(minutes=minutes)

    issued_at = _now()
    claims: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(issued_at.timestamp()),
        "nbf": int(issued_at.timestamp()),
        "exp": int((issued_at + expires_delta).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    if role is not None:
        claims["role"] = role
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str | uuid.UUID, role: str) -> str:
    return create_token(subject, token_type="access", role=role)


def create_refresh_token(subject: str | uuid.UUID, role: str) -> str:
    return create_token(subject, token_type="refresh", role=role)


class TokenError(Exception):
    """Raised when a token is missing, malformed, expired or of the wrong type."""


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Verify signature + expiry and return the claims. Raises ``TokenError``."""
    try:
        claims = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise TokenError("Could not validate credentials") from exc

    if expected_type is not None and claims.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")
    return claims

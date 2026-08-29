"""Human-readable reference generators (report numbers, share tokens)."""

from __future__ import annotations

import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits


def make_reference(prefix: str, length: int = 6) -> str:
    """e.g. ``make_reference("FG-REP")`` -> ``"FG-REP-9K2Q4A"``."""
    body = "".join(secrets.choice(_ALPHABET) for _ in range(length))
    return f"{prefix}-{body}"


def make_share_token(length: int = 40) -> str:
    return secrets.token_urlsafe(length)

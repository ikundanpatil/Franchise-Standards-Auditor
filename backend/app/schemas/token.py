"""Auth request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access-token lifetime in seconds")


class TokenPayload(BaseModel):
    """Decoded JWT claims we care about."""

    sub: str
    role: str | None = None
    type: str | None = None
    exp: int | None = None
    jti: str | None = None


class LoginRequest(BaseModel):
    """JSON login (the OpenAPI ``/auth/login`` form uses OAuth2PasswordRequestForm)."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class RocketRideExchangeRequest(BaseModel):
    """
    Placeholder for the future "Continue with RocketRide" flow: the app would
    POST the shell-issued assertion here and receive a FranchiseGuard ``Token``.
    Not implemented yet — see ``app/routers/auth.py``.
    """

    assertion: str = Field(..., description="Signed identity assertion from the RocketRide shell")

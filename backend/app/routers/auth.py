"""Authentication: register, login, refresh, profile, and admin user management."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession, require_roles
from app.core.exceptions import AppError
from app.models.enums import UserRole
from app.schemas.token import LoginRequest, RefreshRequest, RocketRideExchangeRequest, Token
from app.schemas.user import UserOut, UserRegister, UserRoleUpdate, UserUpdate
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: DbSession) -> UserOut:
    """Create an account. ``role`` is limited to area_manager / inspector / franchise_owner."""
    user = auth_service.register(db, payload)
    return UserOut.model_validate(user)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    """OAuth2 password grant — send the email as ``username``. Powers the Swagger *Authorize* box."""
    user = auth_service.authenticate(db, form.username, form.password)
    auth_service.touch_last_login(db, user)
    return auth_service.issue_tokens(user)


@router.post("/login/json", response_model=Token)
def login_json(payload: LoginRequest, db: DbSession) -> Token:
    """JSON-body login for SPA clients."""
    user = auth_service.authenticate(db, payload.email, payload.password)
    auth_service.touch_last_login(db, user)
    return auth_service.issue_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: DbSession) -> Token:
    return auth_service.rotate_refresh(db, payload.refresh_token)


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, user: CurrentUser, db: DbSession) -> UserOut:
    return UserOut.model_validate(auth_service.update_self(db, user, payload))


@router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def list_users(db: DbSession) -> list[UserOut]:
    return [UserOut.model_validate(u) for u in auth_service.list_users(db)]


@router.patch("/users/{user_id}/role", response_model=UserOut)
def set_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdate,
    actor: Annotated[CurrentUser, Depends(require_roles(UserRole.ADMIN))],
    db: DbSession,
) -> UserOut:
    return UserOut.model_validate(auth_service.set_role(db, actor, user_id, payload))


@router.post("/rocketride", response_model=Token, include_in_schema=True)
def rocketride_exchange(payload: RocketRideExchangeRequest, db: DbSession) -> Token:  # noqa: ARG001
    """
    Exchange a RocketRide shell identity assertion for a FranchiseGuard token.

    Not implemented yet — this is the seam for the "Continue with RocketRide"
    button. Wiring plan: verify ``payload.assertion`` against
    ``settings.ROCKETRIDE_JWKS_URL`` / ``ROCKETRIDE_AUDIENCE``, upsert a ``User``
    keyed by ``external_subject``, then return ``auth_service.issue_tokens(user)``.
    """
    raise AppError(
        "RocketRide identity exchange is not configured on this deployment.",
        code="not_implemented",
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
    )

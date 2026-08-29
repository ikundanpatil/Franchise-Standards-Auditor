"""Authentication and user-account operations."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError, ConflictError, NotFoundError, PermissionDeniedError
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import (
    SELF_ASSIGNABLE_ROLES,
    UserCreate,
    UserRegister,
    UserRoleUpdate,
    UserUpdate,
)
from app.utils.datetime import utcnow


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))


def get_by_id(db: Session, user_id: uuid.UUID | str) -> User | None:
    return db.get(User, user_id)


def require_user(db: Session, user_id: uuid.UUID | str) -> User:
    user = get_by_id(db, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthError("Incorrect email or password")
    if not user.is_active:
        raise AuthError("This account is disabled")
    return user


def register(db: Session, payload: UserRegister) -> User:
    if payload.role not in SELF_ASSIGNABLE_ROLES:
        raise PermissionDeniedError(f"Role {payload.role.value!r} cannot be self-assigned")
    return _create(db, payload, role=payload.role, is_active=True)


def create_user(db: Session, payload: UserCreate) -> User:
    return _create(db, payload, role=payload.role, is_active=payload.is_active)


def _create(
    db: Session, payload: UserRegister | UserCreate, *, role: UserRole, is_active: bool
) -> User:
    if get_by_email(db, payload.email) is not None:
        raise ConflictError("An account with that email already exists")
    user = User(
        email=payload.email.strip().lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        region=payload.region,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_self(db: Session, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data.pop("password"))
    else:
        data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def set_role(db: Session, actor: User, user_id: uuid.UUID, payload: UserRoleUpdate) -> User:
    target = require_user(db, user_id)
    if target.id == actor.id and payload.role != UserRole.ADMIN:
        raise PermissionDeniedError("You cannot remove your own admin role")
    target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return target


def list_users(db: Session):
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


# --- Tokens ----------------------------------------------------------------
def issue_tokens(user: User) -> Token:
    return Token(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id, user.role.value),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def rotate_refresh(db: Session, refresh_token: str) -> Token:
    try:
        claims = decode_token(refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise AuthError(str(exc)) from exc
    user = get_by_id(db, claims["sub"])
    if user is None or not user.is_active:
        raise AuthError("Account no longer valid")
    return issue_tokens(user)


def touch_last_login(db: Session, user: User) -> None:
    user.last_login_at = utcnow()
    db.commit()

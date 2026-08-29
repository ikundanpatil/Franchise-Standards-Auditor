"""
Reusable FastAPI dependencies: DB session, current user, role guards.

Usage in a router::

    @router.get("/things")
    def list_things(user: CurrentUser, db: DbSession): ...

    @router.post("/things", dependencies=[Depends(require_roles(UserRole.ADMIN))])
    def create_thing(...): ...
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError, PermissionDeniedError
from app.core.security import TokenError, decode_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    scheme_name="OAuth2 password (email as username)",
    auto_error=True,
)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        claims = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise AuthError(str(exc)) from exc

    user = auth_service.get_by_id(db, claims["sub"])
    if user is None:
        raise AuthError("User no longer exists")
    if not user.is_active:
        raise AuthError("This account is disabled")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Return a dependency that admits only the given roles (ADMIN always passes)."""
    allowed = set(roles) | {UserRole.ADMIN}

    def _guard(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise PermissionDeniedError(
                "This action requires one of: " + ", ".join(sorted(r.value for r in allowed))
            )
        return user

    return _guard


# Common role bundles.
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
ManagerUser = Annotated[User, Depends(require_roles(UserRole.AREA_MANAGER))]
FieldUser = Annotated[User, Depends(require_roles(UserRole.AREA_MANAGER, UserRole.INSPECTOR))]

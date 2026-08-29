"""User schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole

# Roles a user may self-assign at registration (ADMIN is seed/promote-only).
SELF_ASSIGNABLE_ROLES = {
    UserRole.AREA_MANAGER,
    UserRole.INSPECTOR,
    UserRole.FRANCHISE_OWNER,
}


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    region: str | None = Field(default=None, max_length=80)


class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.INSPECTOR


class UserCreate(UserBase):
    """Admin-side creation — any role allowed."""

    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.INSPECTOR
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    region: str | None = Field(default=None, max_length=80)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRoleUpdate(BaseModel):
    role: UserRole
    is_active: bool | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    phone: str | None
    region: str | None
    last_login_at: datetime | None
    created_at: datetime

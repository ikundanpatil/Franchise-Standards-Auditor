"""User accounts and roles."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.store import Store


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False, length=32, validate_strings=True),
        default=UserRole.INSPECTOR,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Area managers operate a region; used to scope list endpoints.
    region: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Reserved for the future "Continue with RocketRide" bridge: the stable
    # subject id from the shell identity is stored here so a shell user maps to
    # exactly one FranchiseGuard account. Unused today.
    external_subject: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    managed_stores: Mapped[list[Store]] = relationship(
        back_populates="manager",
        foreign_keys="Store.manager_id",
        passive_deletes=True,
    )
    owned_stores: Mapped[list[Store]] = relationship(
        back_populates="owner",
        foreign_keys="Store.owner_id",
        passive_deletes=True,
    )
    inspections: Mapped[list[Inspection]] = relationship(
        back_populates="inspector",
        foreign_keys="Inspection.inspector_id",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.email} ({self.role.value})>"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

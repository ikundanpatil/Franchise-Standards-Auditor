"""Franchise stores (locations) under audit."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import RiskLevel, StoreStatus

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.inspection import Inspection
    from app.models.report import Report
    from app.models.user import User
    from app.models.violation import Violation


class Store(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "stores"

    code: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), default="FranchiseGuard", nullable=False)

    region: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[StoreStatus] = mapped_column(
        SAEnum(StoreStatus, native_enum=False, length=24, validate_strings=True),
        default=StoreStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        SAEnum(RiskLevel, native_enum=False, length=16, validate_strings=True),
        default=RiskLevel.LOW,
        nullable=False,
        index=True,
    )
    compliance_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    # Denormalised cache kept current by the violation service.
    open_violation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    opened_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_inspection_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_inspection_due: Mapped[date | None] = mapped_column(Date, nullable=True)

    manager_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # -- Relationships -------------------------------------------------------
    manager: Mapped[User | None] = relationship(
        back_populates="managed_stores", foreign_keys=[manager_id]
    )
    owner: Mapped[User | None] = relationship(
        back_populates="owned_stores", foreign_keys=[owner_id]
    )
    inspections: Mapped[list[Inspection]] = relationship(
        back_populates="store", passive_deletes=True, order_by="Inspection.created_at.desc()"
    )
    complaints: Mapped[list[Complaint]] = relationship(
        back_populates="store", passive_deletes=True, order_by="Complaint.received_at.desc()"
    )
    violations: Mapped[list[Violation]] = relationship(back_populates="store", passive_deletes=True)
    reports: Mapped[list[Report]] = relationship(
        back_populates="store", passive_deletes=True, order_by="Report.generated_at.desc()"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Store {self.code} {self.name!r}>"

"""Violations — individual compliance findings on an inspection."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import Severity, ViolationStatus

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.store import Store
    from app.models.user import User


class Violation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "violations"

    inspection_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=True, index=True
    )
    store_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Catalogue key, e.g. "v-gloves" (see app/services/ai/catalog.py).
    type_code: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)

    severity: Mapped[Severity] = mapped_column(
        SAEnum(Severity, native_enum=False, length=16, validate_strings=True),
        nullable=False,
        index=True,
    )
    status: Mapped[ViolationStatus] = mapped_column(
        SAEnum(ViolationStatus, native_enum=False, length=24, validate_strings=True),
        default=ViolationStatus.OPEN,
        nullable=False,
        index=True,
    )

    # Null for manually-logged findings; 0..1 for AI detections.
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Normalised [x, y, w, h] in 0..1 image space.
    bounding_box: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)

    standard_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)

    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # -- Relationships -------------------------------------------------------
    inspection: Mapped[Inspection | None] = relationship(back_populates="violations")
    store: Mapped[Store] = relationship(back_populates="violations")
    resolved_by: Mapped[User | None] = relationship(foreign_keys=[resolved_by_id])

    @property
    def is_open(self) -> bool:
        return self.status in (ViolationStatus.OPEN, ViolationStatus.IN_REMEDIATION)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Violation {self.type_code} {self.severity.value} {self.status.value}>"

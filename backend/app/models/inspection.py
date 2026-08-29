"""Inspections — a captured visit to a store, later scored by the AI engine."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import (
    InspectionMethod,
    InspectionSource,
    InspectionStatus,
    RiskLevel,
)

if TYPE_CHECKING:
    from app.models.ai_analysis import AIAnalysis
    from app.models.report import Report
    from app.models.store import Store
    from app.models.user import User
    from app.models.violation import Violation


class Inspection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inspections"

    store_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    inspector_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[InspectionStatus] = mapped_column(
        SAEnum(InspectionStatus, native_enum=False, length=24, validate_strings=True),
        default=InspectionStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    method: Mapped[InspectionMethod] = mapped_column(
        SAEnum(InspectionMethod, native_enum=False, length=24, validate_strings=True),
        default=InspectionMethod.AI_PHOTO,
        nullable=False,
    )
    source: Mapped[InspectionSource] = mapped_column(
        SAEnum(InspectionSource, native_enum=False, length=32, validate_strings=True),
        default=InspectionSource.SCHEDULED,
        nullable=False,
    )

    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # List of {"area": str, "ok": bool, "note": str | None}
    checklist: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    complaint_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    image_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    frame_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # List of {"id": str, "label": str, "kind": "photo"|"video", "url": str | None}
    evidence: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)

    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(
        SAEnum(RiskLevel, native_enum=False, length=16, validate_strings=True), nullable=True
    )
    compliance_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(48), nullable=True)

    # -- Relationships -------------------------------------------------------
    store: Mapped[Store] = relationship(back_populates="inspections")
    inspector: Mapped[User | None] = relationship(
        back_populates="inspections", foreign_keys=[inspector_id]
    )
    violations: Mapped[list[Violation]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan", passive_deletes=True
    )
    report: Mapped[Report | None] = relationship(
        back_populates="inspection",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True,
    )
    analyses: Mapped[list[AIAnalysis]] = relationship(
        back_populates="inspection",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AIAnalysis.created_at.desc()",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Inspection {self.id} store={self.store_id} {self.status.value}>"

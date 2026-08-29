"""Compliance reports — the client-facing rollup of one inspection."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import ReportStatus, RiskLevel

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.store import Store
    from app.models.user import User


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    inspection_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    store_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    reference: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, native_enum=False, length=16, validate_strings=True),
        default=ReportStatus.DRAFT,
        nullable=False,
        index=True,
    )

    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        SAEnum(RiskLevel, native_enum=False, length=16, validate_strings=True), nullable=False
    )
    grade: Mapped[str] = mapped_column(String(2), nullable=False)

    minor_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    major_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    # Each: {"id", "title", "detail", "priority", "owner"}
    recommendations: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    # Each: {"id", "time", "title", "detail", "tone"}
    timeline: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    # Each: {"id", "label", "severity", "tags": [...]}
    evidence: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)

    inspector_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(48), nullable=True)
    generated_by_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pdf_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    share_token: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    shared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # -- Relationships -------------------------------------------------------
    inspection: Mapped[Inspection] = relationship(back_populates="report")
    store: Mapped[Store] = relationship(back_populates="reports")
    generated_by: Mapped[User | None] = relationship(foreign_keys=[generated_by_id])

    @property
    def total_findings(self) -> int:
        return self.minor_count + self.major_count + self.critical_count

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Report {self.reference} {self.risk_level.value}>"

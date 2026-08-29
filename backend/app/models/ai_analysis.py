"""AI analysis runs — one persisted record per vision-engine invocation."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import AIAnalysisStatus, RiskLevel

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.store import Store
    from app.models.user import User


class AIAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_analyses"

    inspection_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=True, index=True
    )
    store_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[AIAnalysisStatus] = mapped_column(
        SAEnum(AIAnalysisStatus, native_enum=False, length=16, validate_strings=True),
        default=AIAnalysisStatus.QUEUED,
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model_version: Mapped[str] = mapped_column(String(48), nullable=False)

    image_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    frame_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(
        SAEnum(RiskLevel, native_enum=False, length=16, validate_strings=True), nullable=True
    )
    # Each: {"type_code", "label", "category", "severity", "confidence",
    #        "bounding_box", "explanation", "standard_ref", "remediation"}
    detections: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    headline: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    requested_by_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # -- Relationships -------------------------------------------------------
    inspection: Mapped[Inspection | None] = relationship(back_populates="analyses")
    store: Mapped[Store] = relationship()
    requested_by: Mapped[User | None] = relationship(foreign_keys=[requested_by_id])

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIAnalysis {self.id} {self.status.value} dets={len(self.detections or [])}>"

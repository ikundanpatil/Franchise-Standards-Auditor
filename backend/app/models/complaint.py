"""Complaints — customer / franchisee reports against a store."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.types import GUID
from app.models.enums import ComplaintChannel, ComplaintStatus, Severity

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.store import Store
    from app.models.user import User


class Complaint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "complaints"

    store_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    channel: Mapped[ComplaintChannel] = mapped_column(
        SAEnum(ComplaintChannel, native_enum=False, length=16, validate_strings=True),
        default=ComplaintChannel.APP,
        nullable=False,
    )
    status: Mapped[ComplaintStatus] = mapped_column(
        SAEnum(ComplaintStatus, native_enum=False, length=20, validate_strings=True),
        default=ComplaintStatus.NEW,
        nullable=False,
        index=True,
    )
    severity: Mapped[Severity | None] = mapped_column(
        SAEnum(Severity, native_enum=False, length=16, validate_strings=True), nullable=True
    )

    reporter_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    reporter_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    triaged_by_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    triaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    linked_inspection_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # -- Relationships -------------------------------------------------------
    store: Mapped[Store] = relationship(back_populates="complaints")
    triaged_by: Mapped[User | None] = relationship(foreign_keys=[triaged_by_id])
    linked_inspection: Mapped[Inspection | None] = relationship(foreign_keys=[linked_inspection_id])

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Complaint {self.id} store={self.store_id} {self.status.value}>"

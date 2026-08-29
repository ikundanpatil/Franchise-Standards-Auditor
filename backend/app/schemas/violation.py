"""Violation schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Severity, ViolationStatus


class ViolationBase(BaseModel):
    type_code: str = Field(..., min_length=1, max_length=48)
    label: str = Field(..., min_length=1, max_length=160)
    category: str = Field(..., min_length=1, max_length=80)
    severity: Severity
    standard_ref: str | None = Field(default=None, max_length=120)
    explanation: str | None = None
    remediation: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    bounding_box: list[float] | None = Field(
        default=None, description="Normalised [x, y, w, h] in 0..1 image space"
    )


class ViolationCreate(ViolationBase):
    """Manually logging a finding against an inspection."""

    due_at: datetime | None = None


class ViolationUpdate(BaseModel):
    status: ViolationStatus | None = None
    severity: Severity | None = None
    remediation: str | None = None
    due_at: datetime | None = None
    resolution_note: str | None = None


class ViolationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inspection_id: uuid.UUID | None
    store_id: uuid.UUID
    type_code: str
    label: str
    category: str
    severity: Severity
    status: ViolationStatus
    confidence: float | None
    bounding_box: list[float] | None
    standard_ref: str | None
    explanation: str | None
    remediation: str | None
    detected_at: datetime
    due_at: datetime | None
    resolved_at: datetime | None
    resolved_by_id: uuid.UUID | None
    resolution_note: str | None
    created_at: datetime

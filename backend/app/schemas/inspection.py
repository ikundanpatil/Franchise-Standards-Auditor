"""Inspection schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    InspectionMethod,
    InspectionSource,
    InspectionStatus,
    RiskLevel,
)
from app.schemas.violation import ViolationOut

CHECKLIST_AREAS = (
    "Kitchen Cleanliness",
    "Staff Hygiene",
    "Food Storage",
    "Branding Compliance",
    "Pest Control",
)


class ChecklistItem(BaseModel):
    area: str = Field(..., description="One of the five brand-standard areas")
    ok: bool = True
    note: str | None = None


class EvidenceItem(BaseModel):
    id: str
    label: str
    kind: str = Field(default="photo", description="photo | video")
    url: str | None = None


class InspectionBase(BaseModel):
    store_id: uuid.UUID
    method: InspectionMethod = InspectionMethod.AI_PHOTO
    source: InspectionSource = InspectionSource.SCHEDULED
    scheduled_for: datetime | None = None
    checklist: list[ChecklistItem] = Field(default_factory=list)
    complaint_text: str | None = None
    image_label: str | None = Field(default=None, max_length=160)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class InspectionCreate(InspectionBase):
    inspector_id: uuid.UUID | None = Field(
        default=None, description="Defaults to the caller when they are an inspector"
    )


class InspectionUpdate(BaseModel):
    status: InspectionStatus | None = None
    method: InspectionMethod | None = None
    scheduled_for: datetime | None = None
    checklist: list[ChecklistItem] | None = None
    complaint_text: str | None = None
    image_label: str | None = Field(default=None, max_length=160)
    evidence: list[EvidenceItem] | None = None


class InspectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    store_id: uuid.UUID
    inspector_id: uuid.UUID | None
    status: InspectionStatus
    method: InspectionMethod
    source: InspectionSource
    scheduled_for: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    checklist: list[ChecklistItem]
    complaint_text: str | None
    image_label: str | None
    frame_count: int
    evidence: list[EvidenceItem]
    risk_score: int | None
    risk_level: RiskLevel | None
    compliance_score: int | None
    summary: str | None
    model_version: str | None
    created_at: datetime
    updated_at: datetime


class InspectionDetail(InspectionOut):
    violations: list[ViolationOut] = Field(default_factory=list)

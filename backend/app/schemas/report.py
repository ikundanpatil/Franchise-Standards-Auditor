"""Compliance-report schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReportStatus, RiskLevel
from app.schemas.violation import ViolationOut


class ReportCounts(BaseModel):
    minor: int = 0
    major: int = 0
    critical: int = 0


class Recommendation(BaseModel):
    id: str
    title: str
    detail: str
    priority: str = Field(..., description="now | soon | monitor")
    owner: str


class TimelineEvent(BaseModel):
    id: str
    time: str
    title: str
    detail: str
    tone: str = "info"


class EvidenceShot(BaseModel):
    id: str
    label: str
    severity: str
    tags: list[str] = Field(default_factory=list)


class ReportGenerateRequest(BaseModel):
    inspection_id: uuid.UUID
    finalize: bool = Field(default=False, description="Mark the report FINAL instead of DRAFT")


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inspection_id: uuid.UUID
    store_id: uuid.UUID
    reference: str
    status: ReportStatus
    risk_score: int
    risk_level: RiskLevel
    grade: str
    minor_count: int
    major_count: int
    critical_count: int
    summary: str
    recommendations: list[Recommendation]
    timeline: list[TimelineEvent]
    evidence: list[EvidenceShot]
    inspector_name: str | None
    model_version: str | None
    generated_by_id: uuid.UUID | None
    generated_at: datetime
    pdf_generated_at: datetime | None
    shared_at: datetime | None
    created_at: datetime


class ReportDetail(ReportOut):
    violations: list[ViolationOut] = Field(default_factory=list)


class ReportShareOut(BaseModel):
    reference: str
    share_token: str
    share_path: str = Field(..., description="Relative link the frontend turns into a URL")
    shared_at: datetime

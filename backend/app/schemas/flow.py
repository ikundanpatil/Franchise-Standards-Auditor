"""Schemas for the end-to-end inspection flow (`/inspection/*`)."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import InspectionStatus
from app.schemas.ai import Detection


class UploadedImage(BaseModel):
    id: str
    filename: str
    stored: bool = Field(..., description="True if pushed to Supabase Storage")
    url: str | None = None
    size: int | None = None


class InspectionUploadResponse(BaseModel):
    inspection_id: uuid.UUID
    store_id: uuid.UUID
    status: InspectionStatus
    images: list[UploadedImage]
    evidence_count: int
    warnings: list[str] = Field(default_factory=list)
    ws_url: str = Field(..., description="Connect here for live progress")


class InspectionAnalyzeRequest(BaseModel):
    inspection_id: uuid.UUID
    complaint_text: str | None = Field(
        default=None, description="Free-text complaint to run through Gemini (optional)"
    )
    background_report: bool = Field(
        default=False, description="Generate the compliance report as a background task"
    )
    save_report_to_supabase: bool = False
    seed: int | None = Field(default=None, description="Deterministic seed for the mock engine")


class RiskResult(BaseModel):
    risk_score: int
    compliance_score: int
    risk_level: str
    counts: dict[str, int]
    breakdown: dict[str, int]


class ComplaintInsight(BaseModel):
    severity: str
    category: str
    summary: str
    urgency: str
    sentiment: str
    requires_inspection: bool
    suggested_actions: list[str]


class ReportRef(BaseModel):
    id: uuid.UUID
    reference: str
    status: str
    pending: bool = False


class InspectionAnalyzeResponse(BaseModel):
    inspection_id: uuid.UUID
    store_id: uuid.UUID
    vision_backend: str
    detections: list[Detection]
    violations_persisted: int
    risk: RiskResult
    complaint_analysis: ComplaintInsight | None = None
    report: ReportRef | None = None
    supabase: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)

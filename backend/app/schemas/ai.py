"""AI analysis schemas — the request/response contract for the vision engine."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AIAnalysisStatus, RiskLevel
from app.schemas.inspection import ChecklistItem


class Detection(BaseModel):
    """One finding produced by the engine (mirrors the frontend ``Detection``)."""

    type_code: str
    label: str
    category: str
    severity: str
    confidence: float = Field(..., ge=0, le=1)
    bounding_box: list[float] = Field(..., description="Normalised [x, y, w, h]")
    explanation: str
    standard_ref: str | None = None
    remediation: str | None = None


class AnalyzeRequest(BaseModel):
    """
    Analyse an existing inspection, or an ad-hoc frame for a store.

    Exactly one of ``inspection_id`` / ``store_id`` is required.
    """

    inspection_id: uuid.UUID | None = None
    store_id: uuid.UUID | None = None
    image_label: str | None = Field(default=None, max_length=160)
    checklist: list[ChecklistItem] | None = None
    persist_violations: bool = Field(
        default=True,
        description="When analysing an inspection, write detections back as Violation rows",
    )
    seed: int | None = Field(default=None, description="Fix the RNG for a reproducible mock run")


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inspection_id: uuid.UUID | None
    store_id: uuid.UUID
    status: AIAnalysisStatus
    provider: str
    model_version: str
    image_label: str | None
    frame_count: int
    risk_score: int | None
    risk_level: RiskLevel | None
    detections: list[Detection]
    headline: str | None
    narrative: str | None
    error: str | None
    requested_by_id: uuid.UUID | None
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    created_at: datetime


class EngineInfo(BaseModel):
    provider: str
    model_version: str
    ready: bool
    simulated: bool
    capabilities: list[str]
    catalog_size: int
    note: str | None = None

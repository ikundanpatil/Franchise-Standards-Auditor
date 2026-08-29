"""Request/response schemas for the external-integration endpoints in ``ai.py``."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.ai import Detection


# --- Gemini: complaint analysis ------------------------------------------------
class ComplaintAnalyzeRequest(BaseModel):
    complaint_id: uuid.UUID | None = Field(
        default=None, description="Analyse a stored complaint (mutually exclusive with `body`)"
    )
    body: str | None = Field(default=None, description="Raw complaint text to analyse")
    store_id: uuid.UUID | None = None
    channel: str | None = None
    persist: bool = Field(
        default=False,
        description="When `complaint_id` is given, write severity + AI tags back to the row",
    )

    @model_validator(mode="after")
    def _one_source(self) -> ComplaintAnalyzeRequest:
        if not self.complaint_id and not (self.body and self.body.strip()):
            raise ValueError("Provide either complaint_id or body")
        return self


class ComplaintAnalysis(BaseModel):
    complaint_id: uuid.UUID | None = None
    severity: str
    category: str
    summary: str
    urgency: str
    sentiment: str
    requires_inspection: bool
    suggested_actions: list[str]
    persisted: bool = False


# --- Gemini: report narrative ------------------------------------------------
class ReportNarrativeRequest(BaseModel):
    inspection_id: uuid.UUID
    save_to_supabase: bool = Field(
        default=False, description="Also persist the generated narrative to Supabase"
    )


class Recommendation(BaseModel):
    title: str
    detail: str
    priority: str
    owner: str


class TimelineEntry(BaseModel):
    time: str
    title: str
    detail: str


class ReportNarrative(BaseModel):
    inspection_id: uuid.UUID
    store_name: str
    risk_score: int
    risk_level: str
    headline: str
    summary: str
    recommendations: list[Recommendation]
    timeline: list[TimelineEntry]
    supabase: dict[str, Any] | None = None


# --- YOLO: vision detection ------------------------------------------------
class VisionDetectResponse(BaseModel):
    inspection_id: uuid.UUID | None = None
    backend: str
    count: int
    detections: list[Detection]
    image: dict[str, Any] | None = None


# --- integration status ------------------------------------------------
class IntegrationsStatus(BaseModel):
    gemini: dict[str, Any]
    supabase: dict[str, Any]
    vision: dict[str, Any]

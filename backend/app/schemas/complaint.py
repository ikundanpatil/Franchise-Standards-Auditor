"""Complaint schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ComplaintChannel, ComplaintStatus, Severity


class ComplaintCreate(BaseModel):
    store_id: uuid.UUID
    channel: ComplaintChannel = ComplaintChannel.APP
    severity: Severity | None = None
    reporter_name: str | None = Field(default=None, max_length=160)
    reporter_contact: str | None = Field(default=None, max_length=255)
    subject: str | None = Field(default=None, max_length=200)
    body: str = Field(..., min_length=1)
    received_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus | None = None
    severity: Severity | None = None
    resolution_note: str | None = None
    linked_inspection_id: uuid.UUID | None = None
    tags: list[str] | None = None


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    store_id: uuid.UUID
    channel: ComplaintChannel
    status: ComplaintStatus
    severity: Severity | None
    reporter_name: str | None
    reporter_contact: str | None
    subject: str | None
    body: str
    received_at: datetime
    triaged_by_id: uuid.UUID | None
    triaged_at: datetime | None
    linked_inspection_id: uuid.UUID | None
    resolution_note: str | None
    resolved_at: datetime | None
    tags: list[str]
    created_at: datetime


class ComplaintTrendBucket(BaseModel):
    week_start: str
    count: int
    resolved: int


class ComplaintTrend(BaseModel):
    store_id: uuid.UUID | None
    buckets: list[ComplaintTrendBucket]
    total: int

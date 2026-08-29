"""Store schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel, StoreStatus
from app.schemas.user import UserOut


class StoreBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=24)
    name: str = Field(..., min_length=1, max_length=160)
    brand: str = Field(default="FranchiseGuard", max_length=80)
    region: str = Field(..., min_length=1, max_length=80)
    address: str = Field(..., min_length=1, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] = Field(default_factory=list)


class StoreCreate(StoreBase):
    status: StoreStatus = StoreStatus.ACTIVE
    risk_level: RiskLevel = RiskLevel.LOW
    compliance_score: int = Field(default=100, ge=0, le=100)
    opened_on: date | None = None
    next_inspection_due: date | None = None
    manager_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None


class StoreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    brand: str | None = Field(default=None, max_length=80)
    region: str | None = Field(default=None, min_length=1, max_length=80)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    latitude: float | None = None
    longitude: float | None = None
    status: StoreStatus | None = None
    risk_level: RiskLevel | None = None
    compliance_score: int | None = Field(default=None, ge=0, le=100)
    next_inspection_due: date | None = None
    manager_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    tags: list[str] | None = None


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    brand: str
    region: str
    address: str
    city: str | None
    country: str | None
    latitude: float | None
    longitude: float | None
    status: StoreStatus
    risk_level: RiskLevel
    compliance_score: int
    open_violation_count: int
    opened_on: date | None
    last_inspection_at: datetime | None
    next_inspection_due: date | None
    manager_id: uuid.UUID | None
    owner_id: uuid.UUID | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class StoreDetail(StoreOut):
    manager: UserOut | None = None
    owner: UserOut | None = None


class RiskPoint(BaseModel):
    date: date
    risk_score: int


class StoreHistory(BaseModel):
    """Powers the frontend Location Memory screen."""

    store_id: uuid.UUID
    risk_series: list[RiskPoint]
    inspections_total: int
    complaints_total: int
    violations_open: int
    violations_resolved: int
    avg_compliance_score: float | None

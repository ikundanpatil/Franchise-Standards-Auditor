"""Schemas for `/dashboard/summary` and `/stores/{id}/risk-history`."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    compliance_score: int
    high_risk_stores: int
    pending_inspections: int
    total_stores: int
    active_stores: int
    open_violations: int
    critical_open_violations: int
    open_complaints: int
    inspections_last_30d: int
    completed_last_30d: int
    reports_last_30d: int


class DashboardSummary(BaseModel):
    generated_at: str
    kpis: DashboardKPIs
    risk_distribution: dict[str, int]
    compliance_trend: list[dict[str, Any]]
    today_inspections: list[dict[str, Any]]
    recent_alerts: list[dict[str, Any]]


class RiskHistoryPoint(BaseModel):
    date: str
    risk_score: int
    compliance_score: int | None = None
    inspection_id: uuid.UUID | None = None


class RiskHistory(BaseModel):
    store_id: uuid.UUID
    window_days: int
    current_risk_level: str
    current_compliance_score: int
    points: list[RiskHistoryPoint]
    violations_open: int
    violations_resolved: int

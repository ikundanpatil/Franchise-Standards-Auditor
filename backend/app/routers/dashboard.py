"""Live dashboard metrics — pure aggregation, always current."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(user: CurrentUser, db: DbSession) -> DashboardSummary:  # noqa: ARG001
    """Network KPIs, risk mix, compliance trend, today's inspections, recent alerts."""
    return DashboardSummary.model_validate(dashboard_service.summary(db))

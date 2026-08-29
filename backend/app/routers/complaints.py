"""Complaints: intake, triage, and trend aggregation."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import ComplaintChannel, ComplaintStatus, Severity, UserRole
from app.schemas.common import Page
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintOut,
    ComplaintTrend,
    ComplaintUpdate,
)
from app.services import complaint_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/complaints", tags=["complaints"])

TriageRoles = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)


@router.get("", response_model=Page[ComplaintOut])
def list_complaints(
    user: CurrentUser,  # noqa: ARG001
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    store_id: uuid.UUID | None = None,
    status_: Annotated[ComplaintStatus | None, Query(alias="status")] = None,
    channel: ComplaintChannel | None = None,
    severity: Severity | None = None,
) -> Page[ComplaintOut]:
    return complaint_service.list_complaints(
        db, params, store_id=store_id, status=status_, channel=channel, severity=severity
    )


@router.get("/trends", response_model=ComplaintTrend)
def complaint_trends(
    user: CurrentUser,  # noqa: ARG001
    db: DbSession,
    store_id: uuid.UUID | None = None,
    weeks: int = Query(12, ge=4, le=52),
) -> ComplaintTrend:
    return ComplaintTrend.model_validate(
        complaint_service.complaint_trend(db, store_id=store_id, weeks=weeks)
    )


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate, user: CurrentUser, db: DbSession) -> ComplaintOut:  # noqa: ARG001
    return ComplaintOut.model_validate(complaint_service.create_complaint(db, payload))


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: uuid.UUID, user: CurrentUser, db: DbSession) -> ComplaintOut:  # noqa: ARG001
    return ComplaintOut.model_validate(complaint_service.get_complaint(db, complaint_id))


@router.patch("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(
    complaint_id: uuid.UUID,
    payload: ComplaintUpdate,
    actor: Annotated[CurrentUser, Depends(TriageRoles)],
    db: DbSession,
) -> ComplaintOut:
    complaint = complaint_service.get_complaint(db, complaint_id)
    return ComplaintOut.model_validate(
        complaint_service.update_complaint(db, complaint, payload, actor)
    )

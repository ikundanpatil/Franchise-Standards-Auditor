"""Violations: cross-store list, detail, and status transitions."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import Severity, UserRole, ViolationStatus
from app.schemas.common import Page
from app.schemas.violation import ViolationOut, ViolationUpdate
from app.services import violation_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/violations", tags=["violations"])

ManageViolations = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)


@router.get("", response_model=Page[ViolationOut])
def list_violations(
    user: CurrentUser,  # noqa: ARG001
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    store_id: uuid.UUID | None = None,
    inspection_id: uuid.UUID | None = None,
    severity: Severity | None = None,
    status_: Annotated[ViolationStatus | None, Query(alias="status")] = None,
    category: str | None = None,
) -> Page[ViolationOut]:
    return violation_service.list_violations(
        db,
        params,
        store_id=store_id,
        inspection_id=inspection_id,
        severity=severity,
        status=status_,
        category=category,
    )


@router.get("/{violation_id}", response_model=ViolationOut)
def get_violation(violation_id: uuid.UUID, user: CurrentUser, db: DbSession) -> ViolationOut:  # noqa: ARG001
    return ViolationOut.model_validate(violation_service.get_violation(db, violation_id))


@router.patch("/{violation_id}", response_model=ViolationOut)
def update_violation(
    violation_id: uuid.UUID,
    payload: ViolationUpdate,
    actor: Annotated[CurrentUser, Depends(ManageViolations)],
    db: DbSession,
) -> ViolationOut:
    violation = violation_service.get_violation(db, violation_id)
    return ViolationOut.model_validate(
        violation_service.update_violation(db, violation, payload, actor)
    )

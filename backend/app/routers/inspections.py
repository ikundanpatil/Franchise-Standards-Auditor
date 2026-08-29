"""Inspections: capture, edit, submit, analyse, and generate a report."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import InspectionStatus, UserRole
from app.schemas.ai import AnalysisOut, AnalyzeRequest
from app.schemas.common import Page
from app.schemas.inspection import (
    InspectionCreate,
    InspectionDetail,
    InspectionOut,
    InspectionUpdate,
)
from app.schemas.report import ReportOut
from app.schemas.violation import ViolationCreate, ViolationOut
from app.services import ai_service, inspection_service, report_service, violation_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/inspections", tags=["inspections"])

FieldRoles = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)


@router.get("", response_model=Page[InspectionOut])
def list_inspections(
    user: CurrentUser,
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    store_id: uuid.UUID | None = None,
    status_: Annotated[InspectionStatus | None, Query(alias="status")] = None,
    inspector_id: uuid.UUID | None = None,
) -> Page[InspectionOut]:
    return inspection_service.list_inspections(
        db, user, params, store_id=store_id, status=status_, inspector_id=inspector_id
    )


@router.post(
    "",
    response_model=InspectionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(FieldRoles)],
)
def create_inspection(payload: InspectionCreate, user: CurrentUser, db: DbSession) -> InspectionOut:
    return InspectionOut.model_validate(inspection_service.create_inspection(db, payload, user))


@router.get("/{inspection_id}", response_model=InspectionDetail)
def get_inspection(inspection_id: uuid.UUID, user: CurrentUser, db: DbSession) -> InspectionDetail:  # noqa: ARG001
    return InspectionDetail.model_validate(
        inspection_service.get_inspection(db, inspection_id, with_violations=True)
    )


@router.patch("/{inspection_id}", response_model=InspectionOut, dependencies=[Depends(FieldRoles)])
def update_inspection(
    inspection_id: uuid.UUID, payload: InspectionUpdate, user: CurrentUser, db: DbSession
) -> InspectionOut:  # noqa: ARG001
    inspection = inspection_service.get_inspection(db, inspection_id)
    return InspectionOut.model_validate(
        inspection_service.update_inspection(db, inspection, payload)
    )


@router.post(
    "/{inspection_id}/submit", response_model=InspectionOut, dependencies=[Depends(FieldRoles)]
)
def submit_inspection(inspection_id: uuid.UUID, user: CurrentUser, db: DbSession) -> InspectionOut:  # noqa: ARG001
    inspection = inspection_service.get_inspection(db, inspection_id)
    return InspectionOut.model_validate(inspection_service.submit_inspection(db, inspection))


@router.get("/{inspection_id}/violations", response_model=list[ViolationOut])
def inspection_violations(
    inspection_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> list[ViolationOut]:  # noqa: ARG001
    inspection = inspection_service.get_inspection(db, inspection_id, with_violations=True)
    return [ViolationOut.model_validate(v) for v in inspection.violations]


@router.post(
    "/{inspection_id}/violations",
    response_model=ViolationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(FieldRoles)],
)
def add_violation(
    inspection_id: uuid.UUID, payload: ViolationCreate, user: CurrentUser, db: DbSession
) -> ViolationOut:  # noqa: ARG001
    inspection = inspection_service.get_inspection(db, inspection_id)
    return ViolationOut.model_validate(violation_service.create_violation(db, inspection, payload))


@router.post(
    "/{inspection_id}/analyze",
    response_model=AnalysisOut,
    dependencies=[Depends(FieldRoles)],
)
def analyze_inspection(
    inspection_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    persist_violations: bool = True,
    seed: int | None = None,
) -> AnalysisOut:
    inspection = inspection_service.get_inspection(db, inspection_id)
    req = AnalyzeRequest(
        inspection_id=inspection.id, persist_violations=persist_violations, seed=seed
    )
    return AnalysisOut.model_validate(ai_service.run_analysis(db, req, user))


@router.post(
    "/{inspection_id}/report",
    response_model=ReportOut,
    dependencies=[Depends(FieldRoles)],
)
def generate_report(
    inspection_id: uuid.UUID, user: CurrentUser, db: DbSession, finalize: bool = False
) -> ReportOut:
    inspection = inspection_service.get_inspection(db, inspection_id, with_violations=True)
    return ReportOut.model_validate(
        report_service.generate_report(db, inspection, user, finalize=finalize)
    )

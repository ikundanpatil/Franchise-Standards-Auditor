"""Compliance reports: list, detail, PDF download, share link."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import ReportStatus, UserRole
from app.schemas.common import Page
from app.schemas.report import (
    ReportDetail,
    ReportGenerateRequest,
    ReportOut,
    ReportShareOut,
)
from app.services import inspection_service, pdf_service, report_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/reports", tags=["reports"])

FieldRoles = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)


@router.get("", response_model=Page[ReportOut])
def list_reports(
    user: CurrentUser,  # noqa: ARG001
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    store_id: uuid.UUID | None = None,
    status_: Annotated[ReportStatus | None, Query(alias="status")] = None,
) -> Page[ReportOut]:
    return report_service.list_reports(db, params, store_id=store_id, status=status_)


@router.post("", response_model=ReportOut, dependencies=[Depends(FieldRoles)])
def generate_report(payload: ReportGenerateRequest, user: CurrentUser, db: DbSession) -> ReportOut:
    inspection = inspection_service.get_inspection(db, payload.inspection_id, with_violations=True)
    return ReportOut.model_validate(
        report_service.generate_report(db, inspection, user, finalize=payload.finalize)
    )


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: uuid.UUID, user: CurrentUser, db: DbSession) -> ReportDetail:  # noqa: ARG001
    return ReportDetail.model_validate(
        report_service.get_report(db, report_id, with_violations=True)
    )


@router.get(
    "/{report_id}/pdf",
    responses={200: {"content": {"application/pdf": {}}, "description": "The report as a PDF"}},
)
def download_report_pdf(report_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Response:  # noqa: ARG001
    report = report_service.get_report(db, report_id)
    pdf = pdf_service.render_report_pdf(report, report.store)
    report_service.mark_pdf_generated(db, report)
    filename = f"{report.reference}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{report_id}/share", response_model=ReportShareOut, dependencies=[Depends(FieldRoles)]
)
def share_report(report_id: uuid.UUID, user: CurrentUser, db: DbSession) -> ReportShareOut:  # noqa: ARG001
    report = report_service.share_report(db, report_service.get_report(db, report_id))
    return ReportShareOut(
        reference=report.reference,
        share_token=report.share_token or "",
        share_path=f"/shared/reports/{report.share_token}",
        shared_at=report.shared_at,  # type: ignore[arg-type]
    )

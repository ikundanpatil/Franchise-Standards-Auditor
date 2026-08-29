"""
End-to-end inspection flow.

    POST /inspection/upload   — create an inspection + push images to Supabase Storage
    POST /inspection/analyze  — YOLO/simulated → violations → Gemini → risk → report
"""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from app.api.deps import CurrentUser, DbSession, require_roles
from app.core.exceptions import ValidationError
from app.models.enums import UserRole
from app.schemas.flow import (
    InspectionAnalyzeRequest,
    InspectionAnalyzeResponse,
    InspectionUploadResponse,
)
from app.services import flow_service

router = APIRouter(prefix="/inspection", tags=["inspection-flow"])

FieldRoles = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)

_MAX_FILES = 8
_MAX_BYTES = 15 * 1024 * 1024


@router.post("/upload", response_model=InspectionUploadResponse)
async def upload_inspection(
    actor: Annotated[CurrentUser, Depends(FieldRoles)],
    db: DbSession,
    store_id: Annotated[str, Form(description="Target store id")],
    images: Annotated[list[UploadFile], File(description="One or more inspection photos")],
    complaint_text: Annotated[str | None, Form()] = None,
    checklist: Annotated[str | None, Form(description="JSON array of checklist items")] = None,
) -> InspectionUploadResponse:
    import uuid as _uuid

    if not images:
        raise ValidationError("At least one image is required")
    if len(images) > _MAX_FILES:
        raise ValidationError(f"At most {_MAX_FILES} images per upload")

    parsed_checklist = None
    if checklist:
        try:
            parsed_checklist = json.loads(checklist)
            if not isinstance(parsed_checklist, list):
                raise ValueError
        except ValueError as exc:
            raise ValidationError("checklist must be a JSON array") from exc

    file_bytes: list[bytes] = []
    for upload in images:
        content = await upload.read()
        if len(content) > _MAX_BYTES:
            raise ValidationError(f"{upload.filename}: exceeds 15MB")
        file_bytes.append(content)

    result = flow_service.create_inspection_with_images(
        db,
        store_id=_uuid.UUID(store_id),
        actor=actor,
        complaint_text=complaint_text,
        checklist=parsed_checklist,
        files=images,
        file_bytes=file_bytes,
    )
    return InspectionUploadResponse.model_validate(result)


@router.post("/analyze", response_model=InspectionAnalyzeResponse)
def analyze_inspection(
    payload: InspectionAnalyzeRequest,
    actor: Annotated[CurrentUser, Depends(FieldRoles)],
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> InspectionAnalyzeResponse:
    """
    Run the full pipeline for a previously-uploaded inspection: vision detection
    → violations persisted → optional Gemini complaint triage → Risk Engine
    compliance score → compliance report (inline or as a background task).
    Live progress streams on ``/api/v1/ws/inspections/{inspection_id}``.
    """
    result = flow_service.run_pipeline(
        db,
        inspection_id=payload.inspection_id,
        actor=actor,
        complaint_text=payload.complaint_text,
        seed=payload.seed,
        background_report=payload.background_report,
        save_report_to_supabase=payload.save_report_to_supabase,
        background_tasks=background_tasks,
    )
    return InspectionAnalyzeResponse.model_validate(result)

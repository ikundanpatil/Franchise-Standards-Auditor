"""
AI analysis endpoints.

``AI_PROVIDER=simulated`` (default) uses the deterministic mock engine. Point it
at a real model by implementing ``app/services/ai/remote.py`` — the request and
response shapes here do not change.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import CurrentUser, DbSession, require_roles
from app.integrations.base import integration_status
from app.models.enums import AIAnalysisStatus, UserRole
from app.schemas.ai import AnalysisOut, AnalyzeRequest, EngineInfo
from app.schemas.common import Page
from app.schemas.integrations import (
    ComplaintAnalysis,
    ComplaintAnalyzeRequest,
    IntegrationsStatus,
    ReportNarrative,
    ReportNarrativeRequest,
    VisionDetectResponse,
)
from app.services import ai_service, integration_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/ai", tags=["ai"])

RunRoles = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER, UserRole.INSPECTOR)


@router.get("/engine", response_model=EngineInfo)
def engine_info(user: CurrentUser) -> EngineInfo:  # noqa: ARG001
    """Report the active engine, model version and capabilities."""
    return EngineInfo.model_validate(ai_service.engine_info())


@router.post("/analyze", response_model=AnalysisOut)
def analyze(
    payload: AnalyzeRequest,
    actor: Annotated[CurrentUser, Depends(RunRoles)],
    db: DbSession,
) -> AnalysisOut:
    """
    Run the vision engine against an inspection (``inspection_id``) or an ad-hoc
    frame for a store (``store_id``). Persists an ``AIAnalysis`` record and, for
    an inspection, writes detections back as violations.
    """
    return AnalysisOut.model_validate(ai_service.run_analysis(db, payload, actor))


@router.get("/analyses", response_model=Page[AnalysisOut])
def list_analyses(
    user: CurrentUser,  # noqa: ARG001
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    store_id: uuid.UUID | None = None,
    inspection_id: uuid.UUID | None = None,
    status_: Annotated[AIAnalysisStatus | None, Query(alias="status")] = None,
) -> Page[AnalysisOut]:
    return ai_service.list_analyses(
        db, params, store_id=store_id, inspection_id=inspection_id, status=status_
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: uuid.UUID, user: CurrentUser, db: DbSession) -> AnalysisOut:  # noqa: ARG001
    return AnalysisOut.model_validate(ai_service.get_analysis(db, analysis_id))


# ===========================================================================
# External integrations — Gemini (text), Supabase (storage/db), YOLO (local).
# Each is configured purely from environment; an unconfigured integration
# returns 503 "integration_not_configured".
# ===========================================================================
@router.get("/integrations", response_model=IntegrationsStatus)
def integrations_status(user: CurrentUser) -> IntegrationsStatus:  # noqa: ARG001
    """Which integrations are wired up (no secrets returned)."""
    return IntegrationsStatus.model_validate(integration_status())


@router.post("/complaints/analyze", response_model=ComplaintAnalysis)
def analyze_complaint(
    payload: ComplaintAnalyzeRequest,
    actor: Annotated[CurrentUser, Depends(RunRoles)],
    db: DbSession,
) -> ComplaintAnalysis:
    """Gemini: triage a complaint (severity, category, urgency, actions)."""
    return ComplaintAnalysis.model_validate(
        integration_service.analyze_complaint(
            db,
            complaint_id=payload.complaint_id,
            body=payload.body,
            store_id=payload.store_id,
            channel=payload.channel,
            persist=payload.persist,
            actor=actor,
        )
    )


@router.post("/reports/generate", response_model=ReportNarrative)
def generate_report_narrative(
    payload: ReportNarrativeRequest,
    actor: Annotated[CurrentUser, Depends(RunRoles)],
    db: DbSession,
) -> ReportNarrative:
    """Gemini: write the narrative + recommendations for an analysed inspection,
    optionally persisting it to Supabase."""
    return ReportNarrative.model_validate(
        integration_service.generate_report_narrative(
            db,
            inspection_id=payload.inspection_id,
            save_to_supabase=payload.save_to_supabase,
            actor=actor,
        )
    )


@router.post("/vision/detect", response_model=VisionDetectResponse)
async def vision_detect(
    actor: Annotated[CurrentUser, Depends(RunRoles)],
    db: DbSession,
    image: Annotated[UploadFile, File(description="Inspection photo (JPEG/PNG)")],
    inspection_id: Annotated[uuid.UUID | None, Form()] = None,
    upload: Annotated[bool, Form(description="Also store the image in Supabase")] = False,
    min_confidence: Annotated[float | None, Form(ge=0, le=1)] = None,
) -> VisionDetectResponse:
    """Local YOLO: detect compliance issues in an uploaded image (no API key).

    With ``inspection_id`` + ``upload=true`` the photo is pushed to Supabase
    Storage and linked on the inspection's evidence list.
    """
    content = await image.read()
    return VisionDetectResponse.model_validate(
        integration_service.detect_in_image(
            db,
            content=content,
            filename=image.filename or "photo.jpg",
            content_type=image.content_type or "image/jpeg",
            inspection_id=inspection_id,
            upload=upload,
            min_confidence=min_confidence,
            actor=actor,
        )
    )

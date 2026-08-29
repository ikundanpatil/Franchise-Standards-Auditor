"""
AI analysis endpoints.

``AI_PROVIDER=simulated`` (default) uses the deterministic mock engine. Point it
at a real model by implementing ``app/services/ai/remote.py`` — the request and
response shapes here do not change.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import AIAnalysisStatus, UserRole
from app.schemas.ai import AnalysisOut, AnalyzeRequest, EngineInfo
from app.schemas.common import Page
from app.services import ai_service
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

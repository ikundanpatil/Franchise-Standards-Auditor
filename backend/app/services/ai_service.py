"""
Orchestration around the vision engine.

Resolves the target store/inspection, invokes the configured engine, persists an
:class:`AIAnalysis` row for every run, and (optionally) folds the detections back
onto the inspection as ``Violation`` rows via ``inspection_service.apply_analysis``.
"""

from __future__ import annotations

import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError, ValidationError
from app.models.ai_analysis import AIAnalysis
from app.models.enums import AIAnalysisStatus
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.schemas.ai import AnalyzeRequest
from app.services import inspection_service
from app.services.ai.engine import AnalysisContext, get_engine
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate


def engine_info() -> dict:
    return get_engine().info()


def list_analyses(
    db: Session,
    params: PageParams,
    *,
    store_id: uuid.UUID | None = None,
    inspection_id: uuid.UUID | None = None,
    status: AIAnalysisStatus | None = None,
) -> dict:
    stmt = select(AIAnalysis)
    if store_id:
        stmt = stmt.where(AIAnalysis.store_id == store_id)
    if inspection_id:
        stmt = stmt.where(AIAnalysis.inspection_id == inspection_id)
    if status:
        stmt = stmt.where(AIAnalysis.status == status)
    stmt = stmt.order_by(AIAnalysis.created_at.desc())
    return paginate(db, stmt, params)


def get_analysis(db: Session, analysis_id: uuid.UUID) -> AIAnalysis:
    analysis = db.get(AIAnalysis, analysis_id)
    if analysis is None:
        raise NotFoundError("Analysis not found")
    return analysis


def run_analysis(db: Session, payload: AnalyzeRequest, actor: User) -> AIAnalysis:
    inspection, store = _resolve_target(db, payload)

    checklist = (
        [item.model_dump() for item in payload.checklist]
        if payload.checklist is not None
        else (inspection.checklist if inspection else [])
    )
    image_label = payload.image_label or (inspection.image_label if inspection else None)

    engine = get_engine()
    analysis = AIAnalysis(
        inspection_id=inspection.id if inspection else None,
        store_id=store.id,
        status=AIAnalysisStatus.RUNNING,
        provider=engine.provider,
        model_version=engine.model_version,
        image_label=image_label,
        frame_count=inspection.frame_count if inspection else 1,
        requested_by_id=actor.id,
        started_at=utcnow(),
        detections=[],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    ctx = AnalysisContext(
        store_id=str(store.id),
        store_name=store.name,
        store_code=store.code,
        store_risk=store.risk_level,
        store_compliance_score=store.compliance_score,
        image_label=image_label or "Kitchen line · station 2",
        checklist=checklist,
        frame_count=analysis.frame_count,
        seed=payload.seed,
    )

    started = time.perf_counter()
    try:
        outcome = engine.analyze(ctx)
    except NotImplementedError as exc:
        analysis.status = AIAnalysisStatus.FAILED
        analysis.error = str(exc)
        analysis.finished_at = utcnow()
        db.commit()
        raise AppError(
            str(exc),
            code="engine_not_ready",
            status_code=501,
            details={"analysis_id": str(analysis.id)},
        ) from exc
    except Exception as exc:  # noqa: BLE001 - record then re-raise as a clean 500-ish
        analysis.status = AIAnalysisStatus.FAILED
        analysis.error = f"{type(exc).__name__}: {exc}"
        analysis.finished_at = utcnow()
        db.commit()
        raise

    analysis.status = AIAnalysisStatus.COMPLETED
    analysis.detections = outcome.detections
    analysis.risk_score = outcome.risk_score
    analysis.risk_level = outcome.risk_level
    analysis.headline = outcome.headline
    analysis.narrative = outcome.narrative
    analysis.image_label = outcome.image_label
    analysis.frame_count = outcome.frame_count
    analysis.finished_at = utcnow()
    analysis.duration_ms = int((time.perf_counter() - started) * 1000)
    db.commit()
    db.refresh(analysis)

    if inspection is not None:
        inspection_service.apply_analysis(
            db, inspection, outcome, persist_violations=payload.persist_violations
        )

    return analysis


def _resolve_target(db: Session, payload: AnalyzeRequest) -> tuple[Inspection | None, Store]:
    if payload.inspection_id is None and payload.store_id is None:
        raise ValidationError("Provide either inspection_id or store_id")

    inspection: Inspection | None = None
    if payload.inspection_id is not None:
        inspection = db.scalar(select(Inspection).where(Inspection.id == payload.inspection_id))
        if inspection is None:
            raise NotFoundError("Inspection not found")

    store_id = payload.store_id or (inspection.store_id if inspection else None)
    store = db.get(Store, store_id) if store_id else None
    if store is None:
        raise NotFoundError("Store not found")
    return inspection, store

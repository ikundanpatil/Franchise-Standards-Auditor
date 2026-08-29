"""
End-to-end inspection pipeline.

    upload image → Supabase Storage → YOLO (or simulated) → violations in Postgres
    → Gemini complaint triage → Risk Engine → compliance report → saved to DB
    → dashboard reflects it on the next read.

Progress is streamed to ``progress_hub`` (WebSocket ``/ws/inspections/{id}``).
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.session import session_scope
from app.integrations import gemini_client, supabase_client, vision_service
from app.integrations.base import IntegrationError
from app.models.ai_analysis import AIAnalysis
from app.models.enums import (
    AIAnalysisStatus,
    InspectionMethod,
    InspectionSource,
    InspectionStatus,
)
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.realtime import progress_hub
from app.schemas.ai import AnalyzeRequest
from app.services import ai_service, inspection_service, report_service, risk_service
from app.services.ai.engine import AnalysisOutcome
from app.utils.datetime import utcnow

logger = get_logger("app.flow")

_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}


# ===========================================================================
# Step 1–2 : create inspection + upload images to Supabase Storage
# ===========================================================================
def create_inspection_with_images(
    db: Session,
    *,
    store_id: uuid.UUID,
    actor: User,
    complaint_text: str | None,
    checklist: list[dict[str, Any]] | None,
    files: list[UploadFile],
    file_bytes: list[bytes],
) -> dict[str, Any]:
    store = db.get(Store, store_id)
    if store is None:
        raise NotFoundError("Store not found")

    inspection = Inspection(
        store_id=store.id,
        inspector_id=actor.id,
        method=InspectionMethod.AI_PHOTO,
        source=InspectionSource.AD_HOC if complaint_text else InspectionSource.SCHEDULED,
        status=InspectionStatus.IN_PROGRESS,
        started_at=utcnow(),
        checklist=checklist or [],
        complaint_text=complaint_text,
        evidence=[],
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    progress_hub.publish(
        str(inspection.id),
        {"stage": "uploading", "progress": 0.05, "message": "storing evidence"},
    )

    images: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    warnings: list[str] = []

    for upload, content in zip(files, file_bytes, strict=False):
        entry_id = uuid.uuid4().hex
        filename = upload.filename or f"{entry_id}.jpg"
        content_type = upload.content_type or "image/jpeg"
        if content_type not in _IMAGE_TYPES:
            warnings.append(f"{filename}: unexpected content-type {content_type}")

        stored = False
        url: str | None = None
        size: int | None = len(content) if content else None
        try:
            result = supabase_client.upload_inspection_image(
                inspection_id=inspection.id,
                filename=filename,
                content=content,
                content_type=content_type,
            )
            stored, url, size = True, result["public_url"], result["size"]
        except IntegrationError as exc:
            warnings.append(f"Supabase upload skipped for {filename}: {exc.message}")

        images.append(
            {"id": entry_id, "filename": filename, "stored": stored, "url": url, "size": size}
        )
        evidence.append(
            {"id": entry_id, "label": filename, "kind": "photo", "url": url, "stored": stored}
        )

    inspection.evidence = evidence
    inspection.frame_count = max(1, len(evidence))
    inspection.image_label = evidence[0]["label"] if evidence else None
    db.commit()
    db.refresh(inspection)

    return {
        "inspection_id": inspection.id,
        "store_id": store.id,
        "status": inspection.status,
        "images": images,
        "evidence_count": len(evidence),
        "warnings": warnings,
        "ws_url": f"{settings.API_V1_PREFIX}/ws/inspections/{inspection.id}",
    }


# ===========================================================================
# Step 3–8 : analyse → violations → complaint triage → risk → report
# ===========================================================================
def run_pipeline(
    db: Session,
    *,
    inspection_id: uuid.UUID,
    actor: User,
    complaint_text: str | None,
    seed: int | None,
    background_report: bool,
    save_report_to_supabase: bool,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    inspection = db.scalar(_inspection_stmt(inspection_id))
    if inspection is None:
        raise NotFoundError("Inspection not found")

    key = str(inspection.id)
    warnings: list[str] = []
    progress_hub.publish(
        key, {"stage": "detecting", "progress": 0.2, "message": "running vision model"}
    )

    # -- Step 3–4 : vision → violations in PostgreSQL -----------------------
    detections, vision_backend, vwarn = _detect(db, inspection, actor, seed)
    warnings.extend(vwarn)
    db.refresh(inspection)

    # -- Step 5 : Gemini complaint analysis -------------------------------
    progress_hub.publish(
        key, {"stage": "complaint", "progress": 0.55, "message": "triaging complaint"}
    )
    text = (complaint_text or inspection.complaint_text or "").strip()
    complaint_insight: dict[str, Any] | None = None
    if text:
        if settings.gemini_configured:
            try:
                complaint_insight = gemini_client.analyze_complaint(
                    text, store_name=inspection.store.name if inspection.store else None
                )
            except IntegrationError as exc:
                warnings.append(f"Gemini complaint analysis failed: {exc.message}")
        else:
            warnings.append("Complaint text supplied but GEMINI_API_KEY is not configured")

    # -- Step 6 : Risk Engine -----------------------------------------------
    progress_hub.publish(
        key, {"stage": "scoring", "progress": 0.7, "message": "calculating compliance score"}
    )
    risk = risk_service.reassess_inspection(
        db,
        inspection,
        complaint_severity=complaint_insight["severity"] if complaint_insight else None,
    )
    db.refresh(inspection)

    # -- Step 7–8 : compliance report -----------------------------------
    progress_hub.publish(key, {"stage": "report", "progress": 0.85, "message": "generating report"})
    report_ref: dict[str, Any] | None = None
    supabase_ref: dict[str, Any] | None = None

    if background_report:
        pending = report_service.ensure_pending(db, inspection, actor)
        background_tasks.add_task(
            _finish_report_task, str(inspection.id), str(actor.id), save_report_to_supabase
        )
        report_ref = {
            "id": pending.id,
            "reference": pending.reference,
            "status": pending.status.value,
            "pending": True,
        }
    else:
        report = report_service.generate_report(db, inspection, actor)
        if save_report_to_supabase:
            supabase_ref = _save_report_to_supabase(inspection, report, actor, warnings)
        report_ref = {
            "id": report.id,
            "reference": report.reference,
            "status": report.status.value,
            "pending": False,
        }

    progress_hub.publish(
        key,
        {
            "stage": "done",
            "progress": 1.0,
            "message": "analysis complete",
            "data": {
                "risk_score": risk.risk_score,
                "compliance_score": risk.compliance_score,
                "risk_level": risk.risk_level.value,
                "violations": sum(risk.counts.values()),
                "report_id": str(report_ref["id"]) if report_ref else None,
                "report_pending": bool(report_ref and report_ref["pending"]),
            },
        },
    )
    # Step 9 — nudge any dashboard listeners to refetch (metrics are live reads).
    progress_hub.publish(
        "dashboard",
        {"stage": "refresh", "message": "inspection analysed", "data": {"inspection_id": key}},
    )

    return {
        "inspection_id": inspection.id,
        "store_id": inspection.store_id,
        "vision_backend": vision_backend,
        "detections": detections,
        "violations_persisted": sum(risk.counts.values()),
        "risk": risk.as_dict(),
        "complaint_analysis": complaint_insight,
        "report": report_ref,
        "supabase": supabase_ref,
        "warnings": warnings,
    }


# --- helpers ------------------------------------------------------------
def _inspection_stmt(inspection_id: uuid.UUID):
    from sqlalchemy import select

    return (
        select(Inspection)
        .where(Inspection.id == inspection_id)
        .options(selectinload(Inspection.violations), selectinload(Inspection.store))
    )


def _detect(
    db: Session, inspection: Inspection, actor: User, seed: int | None
) -> tuple[list[dict[str, Any]], str, list[str]]:
    """Return (detections, backend_used, warnings). Persists violations + AIAnalysis."""
    warnings: list[str] = []

    if settings.VISION_BACKEND == "yolo":
        image_url = next((e.get("url") for e in (inspection.evidence or []) if e.get("url")), None)
        if image_url is None:
            warnings.append("VISION_BACKEND=yolo but no stored image; using simulated engine")
        else:
            try:
                content = supabase_client.fetch_object_bytes(image_url)
                detections = vision_service.analyze_image(content)
                _persist_yolo(db, inspection, detections, actor)
                return detections, "yolo", warnings
            except IntegrationError as exc:
                warnings.append(f"YOLO path failed ({exc.message}); using simulated engine")

    analysis = ai_service.run_analysis(
        db,
        AnalyzeRequest(inspection_id=inspection.id, persist_violations=True, seed=seed),
        actor,
    )
    return list(analysis.detections), analysis.provider, warnings


def _persist_yolo(
    db: Session, inspection: Inspection, detections: list[dict[str, Any]], actor: User
) -> None:
    assessment = risk_service.assess(
        violations=[{"severity": d["severity"]} for d in detections],
        checklist=list(inspection.checklist or []),
    )
    n = len(detections)
    headline = (
        f"YOLO flagged {n} finding{'s' if n != 1 else ''} at "
        f"{inspection.store.name if inspection.store else 'the store'}."
        if n
        else "YOLO found no violations in the uploaded image."
    )
    outcome = AnalysisOutcome(
        provider="yolo",
        model_version=settings.YOLO_MODEL_PATH,
        image_label=inspection.image_label or "uploaded photo",
        frame_count=inspection.frame_count or 1,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        detections=detections,
        headline=headline,
        narrative=headline,
    )
    db.add(
        AIAnalysis(
            inspection_id=inspection.id,
            store_id=inspection.store_id,
            status=AIAnalysisStatus.COMPLETED,
            provider="yolo",
            model_version=settings.YOLO_MODEL_PATH,
            image_label=outcome.image_label,
            frame_count=outcome.frame_count,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            detections=detections,
            headline=headline,
            narrative=headline,
            requested_by_id=actor.id,
            started_at=utcnow(),
            finished_at=utcnow(),
        )
    )
    db.commit()
    inspection_service.apply_analysis(db, inspection, outcome, persist_violations=True)


def _save_report_to_supabase(
    inspection: Inspection, report, actor: User, warnings: list[str]
) -> dict[str, Any] | None:
    try:
        return supabase_client.save_report(
            {
                "report_id": str(report.id),
                "reference": report.reference,
                "inspection_id": str(inspection.id),
                "store_id": str(inspection.store_id),
                "risk_score": report.risk_score,
                "risk_level": report.risk_level.value,
                "grade": report.grade,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "timeline": report.timeline,
                "generated_by": actor.email,
                "generated_at": report.generated_at.isoformat(),
            }
        )
    except IntegrationError as exc:
        warnings.append(f"Supabase save_report skipped: {exc.message}")
        return None


def _finish_report_task(inspection_id: str, actor_id: str, save_to_supabase: bool) -> None:
    """Runs after the response is sent (FastAPI BackgroundTasks)."""
    try:
        with session_scope() as db:
            inspection = db.scalar(_inspection_stmt(uuid.UUID(inspection_id)))
            actor = db.get(User, uuid.UUID(actor_id))
            if inspection is None or actor is None:
                return
            report = report_service.generate_report(db, inspection, actor)
            warnings: list[str] = []
            if save_to_supabase:
                _save_report_to_supabase(inspection, report, actor, warnings)
            progress_hub.publish(
                inspection_id,
                {
                    "stage": "report",
                    "progress": 0.98,
                    "message": "report ready",
                    "data": {
                        "report_id": str(report.id),
                        "reference": report.reference,
                        "status": report.status.value,
                    },
                },
            )
            progress_hub.publish(
                inspection_id, {"stage": "done", "progress": 1.0, "message": "report ready"}
            )
    except Exception:  # noqa: BLE001 - background task must never crash the worker
        logger.exception("background report generation failed for %s", inspection_id)
        progress_hub.publish(
            inspection_id,
            {"stage": "error", "progress": 1.0, "message": "report generation failed"},
        )

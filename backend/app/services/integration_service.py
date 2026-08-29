"""
Glue between the external integrations (``app.integrations``) and the domain.

Keeps ``routers/ai.py`` thin: load/validate DB rows here, call the integration
client, optionally persist the result, return plain dicts for the schemas.
"""

from __future__ import annotations

import contextlib
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.integrations import gemini_client, supabase_client, vision_service
from app.models.enums import ComplaintStatus, Severity
from app.models.user import User
from app.services import complaint_service, inspection_service
from app.utils.datetime import utcnow


# --- Gemini: complaint analysis ------------------------------------------------
def analyze_complaint(
    db: Session,
    *,
    complaint_id: uuid.UUID | None,
    body: str | None,
    store_id: uuid.UUID | None,
    channel: str | None,
    persist: bool,
    actor: User,
) -> dict[str, Any]:
    complaint = None
    store_name: str | None = None

    if complaint_id is not None:
        complaint = complaint_service.get_complaint(db, complaint_id)
        text = complaint.body
        channel = channel or complaint.channel.value
        store_name = complaint.store.name if complaint.store else None
    else:
        text = (body or "").strip()
        if store_id is not None:
            from app.models.store import Store

            store = db.get(Store, store_id)
            store_name = store.name if store else None

    result = gemini_client.analyze_complaint(text, store_name=store_name, channel=channel)

    persisted = False
    if persist and complaint is not None:
        with contextlib.suppress(ValueError):
            complaint.severity = Severity(result["severity"])
        tags = list(complaint.tags or [])
        for tag in (f"ai:{result['category']}", f"urgency:{result['urgency']}"):
            if tag not in tags:
                tags.append(tag)
        complaint.tags = tags
        if complaint.status == ComplaintStatus.NEW:
            complaint.status = ComplaintStatus.TRIAGED
            complaint.triaged_at = utcnow()
            complaint.triaged_by_id = actor.id
        db.commit()
        db.refresh(complaint)
        persisted = True

    return {
        "complaint_id": complaint.id if complaint else None,
        "persisted": persisted,
        **result,
    }


# --- Gemini: report narrative ------------------------------------------------
def generate_report_narrative(
    db: Session, *, inspection_id: uuid.UUID, save_to_supabase: bool, actor: User
) -> dict[str, Any]:
    inspection = inspection_service.get_inspection(db, inspection_id, with_violations=True)
    if inspection.risk_score is None:
        raise ValidationError("Run analysis on this inspection before generating a narrative")

    store_name = inspection.store.name if inspection.store else "the store"
    violations = [
        {
            "label": v.label,
            "category": v.category,
            "severity": v.severity.value,
            "standard_ref": v.standard_ref,
            "confidence": v.confidence,
        }
        for v in inspection.violations
    ]
    narrative = gemini_client.generate_report(
        store_name=store_name,
        risk_score=inspection.risk_score,
        risk_level=(inspection.risk_level.value if inspection.risk_level else "low"),
        violations=violations,
        checklist=list(inspection.checklist or []),
    )

    supabase_ref: dict[str, Any] | None = None
    if save_to_supabase:
        supabase_ref = supabase_client.save_report(
            {
                "inspection_id": str(inspection.id),
                "store_id": str(inspection.store_id),
                "store_name": store_name,
                "risk_score": inspection.risk_score,
                "risk_level": inspection.risk_level.value if inspection.risk_level else "low",
                "headline": narrative["headline"],
                "summary": narrative["summary"],
                "recommendations": narrative["recommendations"],
                "timeline": narrative["timeline"],
                "generated_by": actor.email,
                "generated_at": utcnow().isoformat(),
                "source": "gemini",
            }
        )

    return {
        "inspection_id": inspection.id,
        "store_name": store_name,
        "risk_score": inspection.risk_score,
        "risk_level": inspection.risk_level.value if inspection.risk_level else "low",
        "supabase": supabase_ref,
        **narrative,
    }


# --- YOLO: image detection (+ optional Supabase upload) ---------------------
def detect_in_image(
    db: Session,
    *,
    content: bytes,
    filename: str,
    content_type: str,
    inspection_id: uuid.UUID | None,
    upload: bool,
    min_confidence: float | None,
    actor: User,
) -> dict[str, Any]:
    inspection = None
    if inspection_id is not None:
        inspection = inspection_service.get_inspection(db, inspection_id)

    detections = vision_service.analyze_image(content, min_confidence=min_confidence)

    image_info: dict[str, Any] | None = None
    if upload and inspection is not None:
        image_info = supabase_client.upload_inspection_image(
            inspection_id=inspection.id,
            filename=filename,
            content=content,
            content_type=content_type or "image/jpeg",
        )
        evidence = list(inspection.evidence or [])
        evidence.append(
            {
                "id": uuid.uuid4().hex,
                "label": filename or "inspection photo",
                "kind": "photo",
                "url": image_info["public_url"],
                "added_by": actor.email,
            }
        )
        inspection.evidence = evidence
        inspection.frame_count = max(inspection.frame_count, len(evidence))
        db.commit()

    return {
        "inspection_id": inspection.id if inspection else None,
        "backend": "yolo",
        "count": len(detections),
        "detections": detections,
        "image": image_info,
    }

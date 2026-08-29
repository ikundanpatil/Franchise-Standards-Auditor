"""Inspection lifecycle: create, edit, submit, and apply AI results."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import (
    InspectionStatus,
    RiskLevel,
    UserRole,
    ViolationStatus,
)
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.models.violation import Violation
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services import store_service
from app.services.ai.engine import AnalysisOutcome
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate

_EDITABLE_STATES = {InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS}


def list_inspections(
    db: Session,
    current_user: User,
    params: PageParams,
    *,
    store_id: uuid.UUID | None = None,
    status: InspectionStatus | None = None,
    inspector_id: uuid.UUID | None = None,
) -> dict:
    stmt = select(Inspection)
    if current_user.role == UserRole.FRANCHISE_OWNER:
        owned = select(Store.id).where(Store.owner_id == current_user.id)
        stmt = stmt.where(Inspection.store_id.in_(owned))
    if store_id:
        stmt = stmt.where(Inspection.store_id == store_id)
    if status:
        stmt = stmt.where(Inspection.status == status)
    if inspector_id:
        stmt = stmt.where(Inspection.inspector_id == inspector_id)
    stmt = stmt.order_by(Inspection.created_at.desc())
    return paginate(db, stmt, params)


def get_inspection(
    db: Session, inspection_id: uuid.UUID, *, with_violations: bool = False
) -> Inspection:
    stmt = select(Inspection).where(Inspection.id == inspection_id)
    if with_violations:
        stmt = stmt.options(selectinload(Inspection.violations))
    inspection = db.scalar(stmt)
    if inspection is None:
        raise NotFoundError("Inspection not found")
    return inspection


def create_inspection(db: Session, payload: InspectionCreate, actor: User) -> Inspection:
    store = db.get(Store, payload.store_id)
    if store is None:
        raise NotFoundError("Store not found")

    inspector_id = payload.inspector_id
    if inspector_id is None and actor.role == UserRole.INSPECTOR:
        inspector_id = actor.id

    inspection = Inspection(
        store_id=store.id,
        inspector_id=inspector_id,
        method=payload.method,
        source=payload.source,
        scheduled_for=payload.scheduled_for,
        checklist=[item.model_dump() for item in payload.checklist],
        complaint_text=payload.complaint_text,
        image_label=payload.image_label,
        evidence=[item.model_dump() for item in payload.evidence],
        frame_count=max(1, len(payload.evidence)) if payload.evidence else 1,
        status=InspectionStatus.SCHEDULED,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def update_inspection(db: Session, inspection: Inspection, payload: InspectionUpdate) -> Inspection:
    if inspection.status not in _EDITABLE_STATES and payload.status is None:
        raise ValidationError(f"A {inspection.status.value} inspection can no longer be edited")

    data = payload.model_dump(exclude_unset=True)
    if "checklist" in data and data["checklist"] is not None:
        inspection.checklist = [dict(item) for item in data.pop("checklist")]
    if "evidence" in data and data["evidence"] is not None:
        evidence = [dict(item) for item in data.pop("evidence")]
        inspection.evidence = evidence
        inspection.frame_count = max(1, len(evidence))

    new_status: InspectionStatus | None = data.pop("status", None)
    for key, value in data.items():
        setattr(inspection, key, value)

    if new_status is not None:
        _transition(inspection, new_status)

    db.commit()
    db.refresh(inspection)
    return inspection


def submit_inspection(db: Session, inspection: Inspection) -> Inspection:
    """Mark an inspection ready for analysis."""
    if inspection.status not in _EDITABLE_STATES:
        raise ValidationError("Only a scheduled or in-progress inspection can be submitted")
    inspection.status = InspectionStatus.IN_PROGRESS
    if inspection.started_at is None:
        inspection.started_at = utcnow()
    db.commit()
    db.refresh(inspection)
    return inspection


def _transition(inspection: Inspection, new_status: InspectionStatus) -> None:
    now = utcnow()
    inspection.status = new_status
    if new_status == InspectionStatus.IN_PROGRESS and inspection.started_at is None:
        inspection.started_at = now
    if new_status in (InspectionStatus.COMPLETED, InspectionStatus.CANCELLED):
        inspection.completed_at = now


def apply_analysis(
    db: Session,
    inspection: Inspection,
    outcome: AnalysisOutcome,
    *,
    persist_violations: bool,
) -> Inspection:
    """Fold an :class:`AnalysisOutcome` back onto the inspection (+ its store)."""
    inspection.risk_score = outcome.risk_score
    inspection.risk_level = outcome.risk_level
    inspection.compliance_score = max(0, min(100, 100 - outcome.risk_score))
    inspection.summary = outcome.narrative
    inspection.model_version = outcome.model_version
    inspection.image_label = inspection.image_label or outcome.image_label
    inspection.frame_count = outcome.frame_count
    inspection.status = InspectionStatus.COMPLETED
    inspection.completed_at = utcnow()

    if persist_violations:
        # Replace any prior AI-sourced findings (confidence set); keep manual ones.
        for existing in list(inspection.violations):
            if existing.confidence is not None:
                db.delete(existing)
        db.flush()
        for det in outcome.detections:
            db.add(
                Violation(
                    inspection_id=inspection.id,
                    store_id=inspection.store_id,
                    type_code=det["type_code"],
                    label=det["label"],
                    category=det["category"],
                    severity=det["severity"],
                    status=ViolationStatus.OPEN,
                    confidence=det["confidence"],
                    bounding_box=det["bounding_box"],
                    standard_ref=det.get("standard_ref"),
                    explanation=det.get("explanation"),
                    remediation=det.get("remediation"),
                    detected_at=utcnow(),
                )
            )

    store = db.get(Store, inspection.store_id)
    if store is not None:
        store.last_inspection_at = inspection.completed_at
        store.compliance_score = inspection.compliance_score or store.compliance_score
        if outcome.risk_level:
            store.risk_level = RiskLevel(outcome.risk_level)

    db.commit()
    if store is not None and persist_violations:
        store_service.recompute_risk(db, store)
    db.refresh(inspection)
    return inspection

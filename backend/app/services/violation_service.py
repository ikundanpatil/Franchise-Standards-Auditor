"""Violation queries and lifecycle transitions."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import Severity, ViolationStatus
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.models.violation import Violation
from app.schemas.violation import ViolationCreate, ViolationUpdate
from app.services import store_service
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate

_TERMINAL = {ViolationStatus.RESOLVED, ViolationStatus.WAIVED}


def list_violations(
    db: Session,
    params: PageParams,
    *,
    store_id: uuid.UUID | None = None,
    inspection_id: uuid.UUID | None = None,
    severity: Severity | None = None,
    status: ViolationStatus | None = None,
    category: str | None = None,
) -> dict:
    stmt = select(Violation)
    if store_id:
        stmt = stmt.where(Violation.store_id == store_id)
    if inspection_id:
        stmt = stmt.where(Violation.inspection_id == inspection_id)
    if severity:
        stmt = stmt.where(Violation.severity == severity)
    if status:
        stmt = stmt.where(Violation.status == status)
    if category:
        stmt = stmt.where(Violation.category == category)
    stmt = stmt.order_by(Violation.detected_at.desc())
    return paginate(db, stmt, params)


def get_violation(db: Session, violation_id: uuid.UUID) -> Violation:
    violation = db.get(Violation, violation_id)
    if violation is None:
        raise NotFoundError("Violation not found")
    return violation


def create_violation(db: Session, inspection: Inspection, payload: ViolationCreate) -> Violation:
    violation = Violation(
        inspection_id=inspection.id,
        store_id=inspection.store_id,
        type_code=payload.type_code,
        label=payload.label,
        category=payload.category,
        severity=payload.severity,
        status=ViolationStatus.OPEN,
        confidence=payload.confidence,
        bounding_box=payload.bounding_box,
        standard_ref=payload.standard_ref,
        explanation=payload.explanation,
        remediation=payload.remediation,
        detected_at=utcnow(),
        due_at=payload.due_at,
    )
    db.add(violation)
    db.commit()
    db.refresh(violation)
    _resync_store(db, violation)
    return violation


def update_violation(
    db: Session, violation: Violation, payload: ViolationUpdate, actor: User
) -> Violation:
    data = payload.model_dump(exclude_unset=True)
    new_status: ViolationStatus | None = data.pop("status", None)

    for key, value in data.items():
        setattr(violation, key, value)

    if new_status is not None and new_status != violation.status:
        if violation.status in _TERMINAL and new_status not in _TERMINAL:
            # Re-opening a closed finding.
            violation.resolved_at = None
            violation.resolved_by_id = None
        violation.status = new_status
        if new_status in _TERMINAL:
            violation.resolved_at = utcnow()
            violation.resolved_by_id = actor.id
            if new_status == ViolationStatus.WAIVED and not violation.resolution_note:
                raise ValidationError("A resolution note is required when waiving a violation")

    db.commit()
    db.refresh(violation)
    _resync_store(db, violation)
    return violation


def _resync_store(db: Session, violation: Violation) -> None:
    store = db.get(Store, violation.store_id)
    if store is not None:
        store_service.recompute_risk(db, store)

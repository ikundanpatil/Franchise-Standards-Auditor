"""Complaint intake, triage and trend aggregation."""

from __future__ import annotations

import uuid
from collections import OrderedDict
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.complaint import Complaint
from app.models.enums import ComplaintChannel, ComplaintStatus, Severity
from app.models.store import Store
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate

_RESOLVED = {ComplaintStatus.RESOLVED, ComplaintStatus.DISMISSED}


def list_complaints(
    db: Session,
    params: PageParams,
    *,
    store_id: uuid.UUID | None = None,
    status: ComplaintStatus | None = None,
    channel: ComplaintChannel | None = None,
    severity: Severity | None = None,
) -> dict:
    stmt = select(Complaint)
    if store_id:
        stmt = stmt.where(Complaint.store_id == store_id)
    if status:
        stmt = stmt.where(Complaint.status == status)
    if channel:
        stmt = stmt.where(Complaint.channel == channel)
    if severity:
        stmt = stmt.where(Complaint.severity == severity)
    stmt = stmt.order_by(Complaint.received_at.desc())
    return paginate(db, stmt, params)


def get_complaint(db: Session, complaint_id: uuid.UUID) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise NotFoundError("Complaint not found")
    return complaint


def create_complaint(db: Session, payload: ComplaintCreate) -> Complaint:
    if db.get(Store, payload.store_id) is None:
        raise NotFoundError("Store not found")
    complaint = Complaint(
        store_id=payload.store_id,
        channel=payload.channel,
        severity=payload.severity,
        reporter_name=payload.reporter_name,
        reporter_contact=payload.reporter_contact,
        subject=payload.subject,
        body=payload.body,
        received_at=payload.received_at or utcnow(),
        tags=payload.tags,
        status=ComplaintStatus.NEW,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def update_complaint(
    db: Session, complaint: Complaint, payload: ComplaintUpdate, actor: User
) -> Complaint:
    data = payload.model_dump(exclude_unset=True)
    new_status: ComplaintStatus | None = data.pop("status", None)

    for key, value in data.items():
        setattr(complaint, key, value)

    if new_status is not None and new_status != complaint.status:
        complaint.status = new_status
        if new_status != ComplaintStatus.NEW and complaint.triaged_at is None:
            complaint.triaged_at = utcnow()
            complaint.triaged_by_id = actor.id
        if new_status in _RESOLVED:
            complaint.resolved_at = utcnow()
        else:
            complaint.resolved_at = None

    db.commit()
    db.refresh(complaint)
    return complaint


def complaint_trend(db: Session, *, store_id: uuid.UUID | None, weeks: int = 12) -> dict:
    """Weekly counts for the last ``weeks`` weeks (Location-Memory / dashboard charts)."""
    now = utcnow()
    start = (now - timedelta(weeks=weeks)).replace(hour=0, minute=0, second=0, microsecond=0)
    # Align to Monday.
    start -= timedelta(days=start.weekday())

    stmt = select(Complaint).where(Complaint.received_at >= start)
    if store_id:
        stmt = stmt.where(Complaint.store_id == store_id)
    rows = list(db.scalars(stmt))

    buckets: OrderedDict[str, dict[str, int]] = OrderedDict()
    for i in range(weeks + 1):
        key = (start + timedelta(weeks=i)).date().isoformat()
        buckets[key] = {"count": 0, "resolved": 0}

    for c in rows:
        wk = c.received_at - timedelta(days=c.received_at.weekday())
        key = wk.date().isoformat()
        if key not in buckets:
            continue
        buckets[key]["count"] += 1
        if c.status in _RESOLVED:
            buckets[key]["resolved"] += 1

    return {
        "store_id": store_id,
        "buckets": [
            {"week_start": key, "count": v["count"], "resolved": v["resolved"]}
            for key, v in buckets.items()
        ],
        "total": len(rows),
    }

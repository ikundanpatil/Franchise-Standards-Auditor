"""Store CRUD, access scoping and the Location-Memory rollup."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models.enums import RiskLevel, StoreStatus, UserRole, ViolationStatus
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.models.violation import Violation
from app.schemas.store import StoreCreate, StoreUpdate
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate

_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}


def _visible_stores_stmt(current_user: User) -> Select:
    stmt = select(Store)
    # Franchise owners only ever see stores they own.
    if current_user.role == UserRole.FRANCHISE_OWNER:
        stmt = stmt.where(Store.owner_id == current_user.id)
    return stmt


def list_stores(
    db: Session,
    current_user: User,
    params: PageParams,
    *,
    q: str | None = None,
    region: str | None = None,
    risk_level: RiskLevel | None = None,
    status: StoreStatus | None = None,
    brand: str | None = None,
) -> dict:
    stmt = _visible_stores_stmt(current_user)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            func.lower(Store.name).like(like)
            | func.lower(Store.code).like(like)
            | func.lower(Store.address).like(like)
        )
    if region:
        stmt = stmt.where(Store.region == region)
    if risk_level:
        stmt = stmt.where(Store.risk_level == risk_level)
    if status:
        stmt = stmt.where(Store.status == status)
    if brand:
        stmt = stmt.where(Store.brand == brand)
    stmt = stmt.order_by(Store.risk_level.desc(), Store.name.asc())
    return paginate(db, stmt, params)


def get_store(db: Session, store_id: uuid.UUID, current_user: User) -> Store:
    store = db.get(Store, store_id)
    if store is None:
        raise NotFoundError("Store not found")
    if current_user.role == UserRole.FRANCHISE_OWNER and store.owner_id != current_user.id:
        raise PermissionDeniedError("You do not have access to this store")
    return store


def create_store(db: Session, payload: StoreCreate) -> Store:
    if db.scalar(select(Store).where(Store.code == payload.code)) is not None:
        raise ConflictError(f"Store code {payload.code!r} is already in use")
    store = Store(**payload.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def update_store(db: Session, store: Store, payload: StoreUpdate) -> Store:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(store, key, value)
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store: Store) -> None:
    db.delete(store)
    db.commit()


def recompute_risk(db: Session, store: Store) -> None:
    """Refresh ``open_violation_count`` and nudge ``risk_level`` from open findings."""
    open_count = (
        db.scalar(
            select(func.count(Violation.id)).where(
                Violation.store_id == store.id,
                Violation.status.in_([ViolationStatus.OPEN, ViolationStatus.IN_REMEDIATION]),
            )
        )
        or 0
    )
    store.open_violation_count = int(open_count)

    crit = (
        db.scalar(
            select(func.count(Violation.id)).where(
                Violation.store_id == store.id,
                Violation.status.in_([ViolationStatus.OPEN, ViolationStatus.IN_REMEDIATION]),
                Violation.severity == "critical",
            )
        )
        or 0
    )
    if crit:
        store.risk_level = RiskLevel.CRITICAL
    elif open_count >= 4:
        store.risk_level = RiskLevel.HIGH
    elif open_count >= 1:
        store.risk_level = RiskLevel.MEDIUM
    else:
        store.risk_level = RiskLevel.LOW
    db.commit()


def store_history(db: Session, store: Store, *, days: int = 90) -> dict:
    since = utcnow() - timedelta(days=days)

    rows = db.execute(
        select(Inspection.completed_at, Inspection.risk_score)
        .where(
            Inspection.store_id == store.id,
            Inspection.completed_at.is_not(None),
            Inspection.risk_score.is_not(None),
            Inspection.completed_at >= since,
        )
        .order_by(Inspection.completed_at.asc())
    ).all()
    risk_series = [
        {"date": completed_at.date(), "risk_score": int(score)} for completed_at, score in rows
    ]

    inspections_total = (
        db.scalar(select(func.count(Inspection.id)).where(Inspection.store_id == store.id)) or 0
    )
    from app.models.complaint import Complaint  # local import avoids a cycle at module load

    complaints_total = (
        db.scalar(select(func.count(Complaint.id)).where(Complaint.store_id == store.id)) or 0
    )
    violations_open = (
        db.scalar(
            select(func.count(Violation.id)).where(
                Violation.store_id == store.id,
                Violation.status.in_([ViolationStatus.OPEN, ViolationStatus.IN_REMEDIATION]),
            )
        )
        or 0
    )
    violations_resolved = (
        db.scalar(
            select(func.count(Violation.id)).where(
                Violation.store_id == store.id,
                Violation.status == ViolationStatus.RESOLVED,
            )
        )
        or 0
    )
    avg_score = db.scalar(
        select(func.avg(Inspection.compliance_score)).where(
            Inspection.store_id == store.id, Inspection.compliance_score.is_not(None)
        )
    )

    return {
        "store_id": store.id,
        "risk_series": risk_series,
        "inspections_total": int(inspections_total),
        "complaints_total": int(complaints_total),
        "violations_open": int(violations_open),
        "violations_resolved": int(violations_resolved),
        "avg_compliance_score": round(float(avg_score), 1) if avg_score is not None else None,
    }


def distinct_regions(db: Session) -> list[str]:
    return list(db.scalars(select(Store.region).distinct().order_by(Store.region.asc())))

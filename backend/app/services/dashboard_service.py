"""
Dashboard aggregation.

``summary()`` is a pure live read across every table — no caching — so it always
reflects the most recent analysis (this is how "dashboard metrics automatically
update").
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.enums import (
    ComplaintStatus,
    InspectionStatus,
    RiskLevel,
    Severity,
    StoreStatus,
    ViolationStatus,
)
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.store import Store
from app.models.violation import Violation
from app.utils.datetime import utcnow

_OPEN_VIOLATION = (ViolationStatus.OPEN, ViolationStatus.IN_REMEDIATION)


def summary(db: Session) -> dict[str, Any]:
    now = utcnow()
    since_30d = now - timedelta(days=30)

    total_stores = db.scalar(select(func.count(Store.id))) or 0
    active_stores = (
        db.scalar(select(func.count(Store.id)).where(Store.status == StoreStatus.ACTIVE)) or 0
    )

    avg_compliance = db.scalar(
        select(func.avg(Store.compliance_score)).where(Store.status == StoreStatus.ACTIVE)
    )
    compliance_score = round(float(avg_compliance)) if avg_compliance is not None else 0

    risk_rows = db.execute(
        select(Store.risk_level, func.count(Store.id)).group_by(Store.risk_level)
    ).all()
    risk_distribution = {level.value: 0 for level in RiskLevel}
    for level, count in risk_rows:
        risk_distribution[level.value if hasattr(level, "value") else str(level)] = int(count)
    high_risk_stores = risk_distribution["high"] + risk_distribution["critical"]

    pending_inspections = (
        db.scalar(
            select(func.count(Inspection.id)).where(
                Inspection.status.in_([InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS])
            )
        )
        or 0
    )
    inspections_30d = (
        db.scalar(select(func.count(Inspection.id)).where(Inspection.created_at >= since_30d)) or 0
    )
    completed_30d = (
        db.scalar(
            select(func.count(Inspection.id)).where(
                Inspection.status == InspectionStatus.COMPLETED,
                Inspection.completed_at >= since_30d,
            )
        )
        or 0
    )

    open_violations = (
        db.scalar(select(func.count(Violation.id)).where(Violation.status.in_(_OPEN_VIOLATION)))
        or 0
    )
    critical_open_violations = (
        db.scalar(
            select(func.count(Violation.id)).where(
                Violation.status.in_(_OPEN_VIOLATION),
                Violation.severity == Severity.CRITICAL,
            )
        )
        or 0
    )

    open_complaints = (
        db.scalar(
            select(func.count(Complaint.id)).where(
                Complaint.status.notin_([ComplaintStatus.RESOLVED, ComplaintStatus.DISMISSED])
            )
        )
        or 0
    )
    reports_30d = (
        db.scalar(select(func.count(Report.id)).where(Report.generated_at >= since_30d)) or 0
    )

    return {
        "generated_at": now.isoformat(),
        "kpis": {
            "compliance_score": compliance_score,
            "high_risk_stores": high_risk_stores,
            "pending_inspections": int(pending_inspections),
            "total_stores": int(total_stores),
            "active_stores": int(active_stores),
            "open_violations": int(open_violations),
            "critical_open_violations": int(critical_open_violations),
            "open_complaints": int(open_complaints),
            "inspections_last_30d": int(inspections_30d),
            "completed_last_30d": int(completed_30d),
            "reports_last_30d": int(reports_30d),
        },
        "risk_distribution": risk_distribution,
        "compliance_trend": _compliance_trend(db, months=6),
        "today_inspections": _today_inspections(db, now),
        "recent_alerts": _recent_alerts(db, limit=6),
    }


def _compliance_trend(db: Session, *, months: int) -> list[dict[str, Any]]:
    now = utcnow()
    buckets: list[dict[str, Any]] = []
    for i in range(months - 1, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=32 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        avg = db.scalar(
            select(func.avg(Inspection.compliance_score)).where(
                Inspection.compliance_score.is_not(None),
                Inspection.completed_at >= month_start,
                Inspection.completed_at < month_end,
            )
        )
        buckets.append(
            {
                "month": month_start.strftime("%Y-%m"),
                "compliance_score": round(float(avg)) if avg is not None else None,
            }
        )
    return buckets


def _today_inspections(db: Session, now) -> list[dict[str, Any]]:  # noqa: ANN001
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = db.scalars(
        select(Inspection)
        .where(Inspection.scheduled_for >= start, Inspection.scheduled_for < end)
        .order_by(Inspection.scheduled_for.asc())
        .limit(12)
    ).all()
    out = []
    for ins in rows:
        out.append(
            {
                "inspection_id": str(ins.id),
                "store_id": str(ins.store_id),
                "store_name": ins.store.name if ins.store else None,
                "status": ins.status.value,
                "scheduled_for": ins.scheduled_for.isoformat() if ins.scheduled_for else None,
            }
        )
    return out


def _recent_alerts(db: Session, *, limit: int) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(Violation)
        .where(
            Violation.severity.in_([Severity.CRITICAL, Severity.MAJOR]),
            Violation.status.in_(_OPEN_VIOLATION),
        )
        .order_by(Violation.detected_at.desc())
        .limit(limit)
    ).all()
    alerts = []
    for v in rows:
        alerts.append(
            {
                "id": str(v.id),
                "type": "violation",
                "title": v.label,
                "severity": v.severity.value,
                "store_id": str(v.store_id),
                "store_name": v.store.name if v.store else None,
                "detected_at": v.detected_at.isoformat(),
            }
        )
    return alerts

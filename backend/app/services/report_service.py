"""Compliance-report assembly, retrieval and sharing."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import ReportStatus, RiskLevel, Severity
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.user import User
from app.models.violation import Violation
from app.services.ai.catalog import SEVERITY_WEIGHT
from app.utils.datetime import utcnow
from app.utils.pagination import PageParams, paginate
from app.utils.refs import make_reference, make_share_token

_PRIORITY_BY_SEVERITY = {
    Severity.CRITICAL: "now",
    Severity.MAJOR: "soon",
    Severity.MINOR: "monitor",
}


def score_grade(goodness: int) -> str:
    if goodness >= 90:
        return "A"
    if goodness >= 80:
        return "B"
    if goodness >= 70:
        return "C"
    if goodness >= 55:
        return "D"
    return "F"


def list_reports(
    db: Session,
    params: PageParams,
    *,
    store_id: uuid.UUID | None = None,
    status: ReportStatus | None = None,
) -> dict:
    stmt = select(Report)
    if store_id:
        stmt = stmt.where(Report.store_id == store_id)
    if status:
        stmt = stmt.where(Report.status == status)
    stmt = stmt.order_by(Report.generated_at.desc())
    return paginate(db, stmt, params)


def get_report(db: Session, report_id: uuid.UUID, *, with_violations: bool = False) -> Report:
    stmt = select(Report).where(Report.id == report_id)
    report = db.scalar(stmt)
    if report is None:
        raise NotFoundError("Report not found")
    if with_violations:
        report.__dict__["violations"] = list(
            db.scalars(
                select(Violation)
                .where(Violation.inspection_id == report.inspection_id)
                .order_by(Violation.severity.desc(), Violation.detected_at.asc())
            )
        )
    return report


def get_report_by_token(db: Session, token: str) -> Report:
    report = db.scalar(select(Report).where(Report.share_token == token))
    if report is None:
        raise NotFoundError("Shared report not found")
    return report


def generate_report(
    db: Session, inspection: Inspection, actor: User, *, finalize: bool = False
) -> Report:
    if inspection.risk_score is None:
        raise ValidationError("Run AI analysis on this inspection before generating a report")

    violations = list(
        db.scalars(
            select(Violation)
            .where(Violation.inspection_id == inspection.id)
            .order_by(Violation.severity.desc(), Violation.detected_at.asc())
        )
    )
    counts = {sev: 0 for sev in Severity}
    for v in violations:
        counts[v.severity] += 1

    goodness = max(0, min(100, 100 - inspection.risk_score))
    store = inspection.store

    payload = {
        "reference": make_reference("FG-REP"),
        "store_id": inspection.store_id,
        "risk_score": inspection.risk_score,
        "risk_level": inspection.risk_level or RiskLevel.LOW,
        "grade": score_grade(goodness),
        "minor_count": counts[Severity.MINOR],
        "major_count": counts[Severity.MAJOR],
        "critical_count": counts[Severity.CRITICAL],
        "summary": inspection.summary or _fallback_summary(store.name, violations),
        "recommendations": _recommendations(violations, store.name),
        "timeline": _timeline(inspection, violations),
        "evidence": _evidence(violations),
        "inspector_name": inspection.inspector.full_name if inspection.inspector else None,
        "model_version": inspection.model_version,
        "generated_by_id": actor.id,
        "generated_at": utcnow(),
        "status": ReportStatus.FINAL if finalize else ReportStatus.DRAFT,
    }

    existing = db.scalar(select(Report).where(Report.inspection_id == inspection.id))
    if existing is not None:
        for key, value in payload.items():
            setattr(existing, key, value)
        report = existing
    else:
        report = Report(inspection_id=inspection.id, **payload)
        db.add(report)

    db.commit()
    db.refresh(report)
    return report


def share_report(db: Session, report: Report) -> Report:
    if report.share_token is None:
        report.share_token = make_share_token()
    report.shared_at = utcnow()
    db.commit()
    db.refresh(report)
    return report


def mark_pdf_generated(db: Session, report: Report) -> None:
    report.pdf_generated_at = utcnow()
    db.commit()


# --- rollup helpers (ported from the frontend's src/lib/ai.ts) --------------
def _fallback_summary(store_name: str, violations: list[Violation]) -> str:
    if not violations:
        return f"{store_name} is within brand standard on every checked area this cycle."
    return (
        f"{len(violations)} finding(s) logged at {store_name}. See the recommendations below "
        "for the remediation order."
    )


def _recommendations(violations: list[Violation], store_name: str) -> list[dict]:
    if not violations:
        return [
            {
                "id": "rec-hold",
                "title": "Maintain current routine",
                "detail": f"{store_name} is clear this cycle. Keep mid-shift checks and daily logs running.",
                "priority": "monitor",
                "owner": "Store Manager",
            }
        ]
    ordered = sorted(violations, key=lambda v: SEVERITY_WEIGHT[v.severity], reverse=True)
    recs: list[dict] = []
    for i, v in enumerate(ordered[:4]):
        recs.append(
            {
                "id": f"rec-{v.id}",
                "title": (v.remediation or v.label).split(".")[0].strip(),
                "detail": f"{v.label} · {v.standard_ref or 'brand standard'}. {v.remediation or ''}".strip(),
                "priority": _PRIORITY_BY_SEVERITY[v.severity],
                "owner": "Store Manager" if i == 0 else "Shift Lead",
            }
        )
    if any(v.severity == Severity.CRITICAL for v in violations):
        recs.append(
            {
                "id": "rec-reinspect",
                "title": "Book a 72-hour re-inspection",
                "detail": "Schedule an AI photo re-check to confirm the critical items are closed.",
                "priority": "now",
                "owner": "Area Manager",
            }
        )
    return recs


def _timeline(inspection: Inspection, violations: list[Violation]) -> list[dict]:
    events = [
        {
            "id": "t-upload",
            "time": "T-0",
            "title": "Evidence uploaded",
            "detail": f"{inspection.frame_count} frame(s) from {inspection.image_label or 'the store floor'}.",
            "tone": "info",
        },
        {
            "id": "t-scan",
            "time": "+18s",
            "title": "Vision model completed",
            "detail": f"{len(violations)} finding(s) · model {inspection.model_version or 'fg-vision'}.",
            "tone": "violet",
        },
    ]
    if any(v.severity == Severity.CRITICAL for v in violations):
        events.append(
            {
                "id": "t-alert",
                "time": "+20s",
                "title": "Critical alert raised",
                "detail": "Pushed to the store manager and the Area Manager queue.",
                "tone": "risk",
            }
        )
    events.append(
        {
            "id": "t-report",
            "time": "+34s",
            "title": "Compliance report generated",
            "detail": "Ready to download or share with the franchisee.",
            "tone": "good",
        }
    )
    return events


def _evidence(violations: list[Violation]) -> list[dict]:
    if not violations:
        return [
            {
                "id": "ev-clean-1",
                "label": "Prep line — clear",
                "severity": "minor",
                "tags": ["Reference", "Pass"],
            },
            {
                "id": "ev-clean-2",
                "label": "Cold well — in range",
                "severity": "minor",
                "tags": ["3°C", "Pass"],
            },
        ]
    return [
        {
            "id": f"ev-{v.id}",
            "label": v.label,
            "severity": v.severity.value,
            "tags": [v.category, f"{round((v.confidence or 0) * 100)}%"],
        }
        for v in violations
    ]

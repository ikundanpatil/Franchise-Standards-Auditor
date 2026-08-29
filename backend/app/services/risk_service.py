"""
Risk Engine — turns findings into a compliance score.

A single, documented, testable calculation used by the end-to-end flow
(``flow_service``) after violations have been persisted. It is deliberately
transparent: severity-weighted violations + failed checklist areas + an optional
complaint-severity bump, mapped onto a 0–100 compliance score and a risk band.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import RiskLevel, Severity, ViolationStatus
from app.models.inspection import Inspection
from app.models.store import Store
from app.services import store_service

# Per-open-violation weight (aligns with app/services/ai/catalog.SEVERITY_WEIGHT).
SEVERITY_WEIGHT: dict[str, int] = {"minor": 6, "major": 16, "critical": 34}
CHECKLIST_FAIL_PENALTY = 4
COMPLAINT_BUMP: dict[str, int] = {"minor": 3, "major": 8, "critical": 16}


@dataclass(slots=True)
class RiskAssessment:
    risk_score: int  # 0 (clean) … 100 (severe)
    compliance_score: int  # 100 - risk_score
    risk_level: RiskLevel
    counts: dict[str, int] = field(default_factory=dict)  # severity -> n
    breakdown: dict[str, int] = field(default_factory=dict)  # contribution by factor

    def as_dict(self) -> dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "compliance_score": self.compliance_score,
            "risk_level": self.risk_level.value,
            "counts": self.counts,
            "breakdown": self.breakdown,
        }


def band(compliance_score: int) -> RiskLevel:
    """Compliance score (higher = better) → risk band."""
    if compliance_score >= 85:
        return RiskLevel.LOW
    if compliance_score >= 70:
        return RiskLevel.MEDIUM
    if compliance_score >= 50:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def assess(
    *,
    violations: list[dict[str, Any]],
    checklist: list[dict[str, Any]] | None = None,
    complaint_severity: str | None = None,
) -> RiskAssessment:
    """
    Pure function — no DB. ``violations`` items need at least ``severity`` and
    (optionally) ``status``; resolved/waived findings do not count.
    """
    counts = {s.value: 0 for s in Severity}
    violation_points = 0
    for v in violations:
        status = str(v.get("status", ViolationStatus.OPEN.value))
        if status in (ViolationStatus.RESOLVED.value, ViolationStatus.WAIVED.value):
            continue
        sev = str(v.get("severity", "minor"))
        if sev in counts:
            counts[sev] += 1
        violation_points += SEVERITY_WEIGHT.get(sev, SEVERITY_WEIGHT["minor"])

    failed_areas = sum(1 for item in (checklist or []) if item.get("ok") is False)
    checklist_points = failed_areas * CHECKLIST_FAIL_PENALTY

    complaint_points = COMPLAINT_BUMP.get(str(complaint_severity), 0) if complaint_severity else 0

    risk_score = _clamp(violation_points + checklist_points + complaint_points)
    compliance_score = 100 - risk_score
    return RiskAssessment(
        risk_score=risk_score,
        compliance_score=compliance_score,
        risk_level=band(compliance_score),
        counts=counts,
        breakdown={
            "violations": violation_points,
            "checklist": checklist_points,
            "complaint": complaint_points,
        },
    )


def reassess_inspection(
    db: Session, inspection: Inspection, *, complaint_severity: str | None = None
) -> RiskAssessment:
    """
    Recompute from the inspection's *persisted* violations + checklist, write the
    result onto the inspection and its store, and return the assessment.
    """
    violations = [
        {"severity": v.severity.value, "status": v.status.value} for v in inspection.violations
    ]
    result = assess(
        violations=violations,
        checklist=list(inspection.checklist or []),
        complaint_severity=complaint_severity,
    )

    inspection.risk_score = result.risk_score
    inspection.risk_level = result.risk_level
    inspection.compliance_score = result.compliance_score

    store = db.get(Store, inspection.store_id)
    if store is not None:
        store.compliance_score = result.compliance_score
        store.risk_level = result.risk_level

    db.commit()
    if store is not None:
        store_service.recompute_risk(db, store)
    db.refresh(inspection)
    return result

"""
The violation catalogue and checklist areas.

Mirrors the frontend's ``src/data/violations.ts`` and ``src/data/checklist.ts``
so the two sides agree on codes, labels, categories and standard references.
A real vision model would emit ``type_code`` values from this same set.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.enums import Severity


@dataclass(frozen=True, slots=True)
class ViolationSpec:
    code: str
    label: str
    category: str
    severity: Severity
    box: tuple[float, float, float, float]  # normalised [x, y, w, h]
    rationale: str
    standard_ref: str
    remediation: str


VIOLATION_CATALOG: tuple[ViolationSpec, ...] = (
    ViolationSpec(
        code="v-gloves",
        label="Missing Gloves",
        category="Staff Hygiene",
        severity=Severity.CRITICAL,
        box=(0.52, 0.28, 0.22, 0.26),
        rationale=(
            "bare hands detected in the food-prep zone with no visible glove line at the "
            "wrist; direct ready-to-eat contact is likely"
        ),
        standard_ref="BSM 4.2 · Hand protection during RTE prep",
        remediation="Re-brief shift on glove policy; place dispensers at every prep station.",
    ),
    ViolationSpec(
        code="v-floor",
        label="Dirty Kitchen Floor",
        category="Kitchen Cleanliness",
        severity=Severity.MAJOR,
        box=(0.08, 0.66, 0.44, 0.28),
        rationale=(
            "standing liquid and debris across the line-side floor with a visible spread "
            "pattern near the fryer"
        ),
        standard_ref="BSM 2.1 · Floors clean, dry, unobstructed",
        remediation="Immediate spot-clean; add mid-shift floor check to the cleaning rota.",
    ),
    ViolationSpec(
        code="v-label",
        label="Expired Food Label",
        category="Food Storage",
        severity=Severity.CRITICAL,
        box=(0.60, 0.55, 0.20, 0.22),
        rationale=(
            "day-dot label on the container reads two days past its use-by; product remains "
            "in the cold well"
        ),
        standard_ref="BSM 3.4 · Date marking & stock rotation",
        remediation="Discard affected stock now; audit the full cold well and re-date.",
    ),
    ViolationSpec(
        code="v-uncovered",
        label="Food Left Uncovered",
        category="Food Storage",
        severity=Severity.MAJOR,
        box=(0.28, 0.34, 0.24, 0.20),
        rationale=(
            "open tray of prepared product on the counter with no lid or film and no active "
            "service in frame"
        ),
        standard_ref="BSM 3.2 · Product protection when not in service",
        remediation="Cover and return to chilled storage; retrain on holding rules.",
    ),
    ViolationSpec(
        code="v-signage",
        label="Non-compliant Signage",
        category="Branding Compliance",
        severity=Severity.MINOR,
        box=(0.05, 0.06, 0.30, 0.16),
        rationale=(
            "menu board uses a superseded logo lockup and off-palette colour vs. the current "
            "brand kit"
        ),
        standard_ref="BRAND 1.1 · Approved signage & lockups",
        remediation="Order the current board pack; remove legacy artwork within 14 days.",
    ),
    ViolationSpec(
        code="v-handwash",
        label="Handwash Sink Blocked",
        category="Staff Hygiene",
        severity=Severity.MAJOR,
        box=(0.74, 0.40, 0.20, 0.34),
        rationale="dedicated handwash basin is stacked with utensils, reducing access during service",
        standard_ref="BSM 4.1 · Handwash stations kept clear",
        remediation="Clear the basin; mark it hands-only with fresh signage.",
    ),
    ViolationSpec(
        code="v-pest",
        label="Pest Entry Point",
        category="Pest Control",
        severity=Severity.MAJOR,
        box=(0.82, 0.72, 0.14, 0.20),
        rationale="gap under the rear door with no brush seal; daylight visible along the threshold",
        standard_ref="BSM 6.3 · Proofing of external openings",
        remediation="Fit a brush strip; log with the pest contractor on next visit.",
    ),
    ViolationSpec(
        code="v-temp",
        label="Cold-Hold Above Range",
        category="Food Storage",
        severity=Severity.CRITICAL,
        box=(0.42, 0.50, 0.20, 0.24),
        rationale=(
            "display unit thermometer reads 9°C against a 0–5°C standard; condensation on "
            "the glass"
        ),
        standard_ref="BSM 3.1 · Cold holding 5°C or below",
        remediation="Move stock to a working unit; call refrigeration; record corrective action.",
    ),
    ViolationSpec(
        code="v-waste",
        label="Overflowing Waste Bin",
        category="Kitchen Cleanliness",
        severity=Severity.MINOR,
        box=(0.12, 0.44, 0.16, 0.30),
        rationale="open bin past fill line beside the prep bench with no lid in place",
        standard_ref="BSM 2.4 · Waste stored in lidded containers",
        remediation="Empty now; add a lidded bin and a mid-shift empty step.",
    ),
    ViolationSpec(
        code="v-uniform",
        label="Uniform Not to Spec",
        category="Branding Compliance",
        severity=Severity.MINOR,
        box=(0.50, 0.12, 0.18, 0.40),
        rationale="crew member in a non-issued top with no name badge or apron",
        standard_ref="BRAND 2.3 · Crew uniform standard",
        remediation="Issue correct uniform; badge every crew member on shift.",
    ),
)

CATALOG_BY_CODE: dict[str, ViolationSpec] = {v.code: v for v in VIOLATION_CATALOG}

# The five brand-standard areas scored on every inspection.
CHECKLIST_AREAS: tuple[str, ...] = (
    "Kitchen Cleanliness",
    "Staff Hygiene",
    "Food Storage",
    "Branding Compliance",
    "Pest Control",
)

SEVERITY_WEIGHT: dict[Severity, int] = {
    Severity.MINOR: 6,
    Severity.MAJOR: 16,
    Severity.CRITICAL: 34,
}

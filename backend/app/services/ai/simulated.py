"""
Deterministic mock vision engine.

A faithful port of the frontend's ``src/lib/ai.ts``: it stitches templated
language over the violation catalogue, rolls randomised confidence scores and
returns a believable risk rollup. Pass ``ctx.seed`` for a reproducible run.

Swap this for a real model by implementing :class:`VisionAnalysisEngine` in
``app/services/ai/remote.py`` and setting ``AI_PROVIDER``.
"""

from __future__ import annotations

import random
import time

from app.core.config import settings
from app.models.enums import RiskLevel, Severity
from app.services.ai.catalog import (
    CATALOG_BY_CODE,
    SEVERITY_WEIGHT,
    VIOLATION_CATALOG,
    ViolationSpec,
)
from app.services.ai.engine import AnalysisContext, AnalysisOutcome

_LEAD_PHRASES = (
    "Detected with high spatial confidence",
    "Flagged by the vision model",
    "Identified in the uploaded frame",
    "Model attention concentrated here",
)
_TAIL_PHRASES = (
    "Matches known non-conformance patterns from comparable sites.",
    "Consistent with prior findings at similar locations.",
    "No mitigating context detected in surrounding pixels.",
    "Bounding region isolated from active-service cues.",
)

_COUNT_BY_RISK: dict[RiskLevel, tuple[int, int]] = {
    RiskLevel.LOW: (0, 2),
    RiskLevel.MEDIUM: (2, 3),
    RiskLevel.HIGH: (3, 5),
    RiskLevel.CRITICAL: (4, 6),
}


def risk_from_goodness(score: float) -> RiskLevel:
    """Map a 0..100 'goodness' score to a risk band (higher score => lower risk)."""
    if score >= 85:
        return RiskLevel.LOW
    if score >= 70:
        return RiskLevel.MEDIUM
    if score >= 50:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class SimulatedVisionEngine:
    provider = "simulated"
    simulated = True

    def __init__(self) -> None:
        self.model_version = settings.AI_MODEL_VERSION

    # -- public API -------------------------------------------------------
    def analyze(self, ctx: AnalysisContext) -> AnalysisOutcome:
        self._simulate_latency()
        rng = random.Random(ctx.seed) if ctx.seed is not None else random.Random()

        specs = self._choose_violations(ctx.store_risk, rng)
        detections = [self._detection(spec, rng) for spec in specs]

        raw_risk = sum(SEVERITY_WEIGHT[Severity(d["severity"])] for d in detections)
        risk_score = int(_clamp(round(raw_risk + (100 - ctx.store_compliance_score) * 0.25), 4, 96))
        risk_level = risk_from_goodness(100 - risk_score)
        frame_count = ctx.frame_count or rng.randint(1, 4)

        return AnalysisOutcome(
            provider=self.provider,
            model_version=self.model_version,
            image_label=ctx.image_label,
            frame_count=frame_count,
            risk_score=risk_score,
            risk_level=risk_level,
            detections=detections,
            headline=self._headline(detections, ctx.store_name),
            narrative=self._narrative(detections, ctx.store_name, risk_score),
        )

    def info(self) -> dict:
        return {
            "provider": self.provider,
            "model_version": self.model_version,
            "ready": True,
            "simulated": True,
            "capabilities": ["detection", "risk_scoring", "narrative", "recommendations"],
            "catalog_size": len(VIOLATION_CATALOG),
            "note": "Deterministic mock engine — no external model call.",
        }

    # -- internals -------------------------------------------------------
    def _simulate_latency(self) -> None:
        ms = max(0, settings.AI_SIMULATED_LATENCY_MS)
        if ms:
            time.sleep(ms / 1000)

    def _choose_violations(self, store_risk: RiskLevel, rng: random.Random) -> list[ViolationSpec]:
        low, high = _COUNT_BY_RISK.get(store_risk, (2, 4))
        count = rng.randint(low, high)
        if count <= 0:
            return []

        weighted: list[ViolationSpec] = []
        for spec in VIOLATION_CATALOG:
            base = {Severity.CRITICAL: 3, Severity.MAJOR: 2, Severity.MINOR: 1}[spec.severity]
            if store_risk == RiskLevel.LOW:
                boost = 1
            elif store_risk == RiskLevel.CRITICAL:
                boost = base
            else:
                boost = max(1, -(-base // 2))  # ceil(base / 2)
            weighted.extend([spec] * boost)

        rng.shuffle(weighted)
        chosen: list[ViolationSpec] = []
        seen: set[str] = set()
        for spec in weighted:
            if spec.code in seen:
                continue
            seen.add(spec.code)
            chosen.append(spec)
            if len(chosen) == count:
                break
        return chosen

    def _detection(self, spec: ViolationSpec, rng: random.Random) -> dict:
        conf_floor = 0.70 if spec.severity == Severity.MINOR else 0.80
        confidence = round(rng.uniform(conf_floor, 0.98), 2)
        x, y, w, h = spec.box
        box = [
            round(_clamp(x + rng.uniform(-0.03, 0.03), 0.0, 0.9), 3),
            round(_clamp(y + rng.uniform(-0.03, 0.03), 0.0, 0.9), 3),
            round(_clamp(w * rng.uniform(0.92, 1.04), 0.08, 0.5), 3),
            round(_clamp(h * rng.uniform(0.92, 1.04), 0.08, 0.5), 3),
        ]
        lead = rng.choice(_LEAD_PHRASES)
        tail = rng.choice(_TAIL_PHRASES)
        rationale = spec.rationale[0].upper() + spec.rationale[1:]
        explanation = f"{lead} ({round(confidence * 100)}%). {rationale}. {tail}"
        return {
            "type_code": spec.code,
            "label": spec.label,
            "category": spec.category,
            "severity": spec.severity.value,
            "confidence": confidence,
            "bounding_box": box,
            "explanation": explanation,
            "standard_ref": spec.standard_ref,
            "remediation": spec.remediation,
        }

    def _headline(self, detections: list[dict], store_name: str) -> str:
        if not detections:
            return f"No violations detected at {store_name} — store is within standard."
        crit = sum(1 for d in detections if d["severity"] == Severity.CRITICAL.value)
        major = sum(1 for d in detections if d["severity"] == Severity.MAJOR.value)
        if crit:
            return f"{crit} critical finding{'s' if crit > 1 else ''} at {store_name} need same-day action."
        if major:
            return f"{major} major finding{'s' if major > 1 else ''} at {store_name} to correct this week."
        return f"{len(detections)} minor finding{'s' if len(detections) > 1 else ''} logged at {store_name}."

    def _narrative(self, detections: list[dict], store_name: str, risk_score: int) -> str:
        if not detections:
            return (
                f"The model reviewed the upload against all five brand-standard areas and found "
                f"no non-conformances. {store_name} continues to track above the network average "
                f"— keep the current routine in place."
            )
        categories = sorted({d["category"] for d in detections})
        worst = max(detections, key=lambda d: SEVERITY_WEIGHT[Severity(d["severity"])])
        band = risk_from_goodness(100 - risk_score)
        band_line = {
            RiskLevel.CRITICAL: "This places the store in the severe band; manager intervention is required today.",
            RiskLevel.HIGH: "This lifts the store into the high-risk band; a re-inspection within 72 hours is advised.",
            RiskLevel.MEDIUM: "The store sits in the moderate band; corrective actions should close within the week.",
            RiskLevel.LOW: "Overall exposure stays low; address the items at the next routine visit.",
        }[band]
        n = len(detections)
        return (
            f"The model surfaced {n} finding{'s' if n > 1 else ''} spanning {len(categories)} "
            f"area{'s' if len(categories) > 1 else ''} ({', '.join(categories)}). The most "
            f"significant is \"{worst['label']}\" at {round(worst['confidence'] * 100)}% "
            f"confidence. {band_line}"
        )


__all__ = ["SimulatedVisionEngine", "risk_from_goodness", "CATALOG_BY_CODE"]

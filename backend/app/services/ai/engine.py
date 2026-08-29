"""Engine interface, shared value objects and the provider factory."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.core.config import settings
from app.models.enums import RiskLevel


@dataclass(slots=True)
class AnalysisContext:
    """Everything an engine needs to score one capture."""

    store_id: str
    store_name: str
    store_code: str
    store_risk: RiskLevel
    store_compliance_score: int
    image_label: str = "Kitchen line · station 2"
    checklist: list[dict] = field(default_factory=list)
    frame_count: int | None = None
    seed: int | None = None


@dataclass(slots=True)
class AnalysisOutcome:
    """Engine-agnostic result. ``detections`` items match ``schemas.ai.Detection``."""

    provider: str
    model_version: str
    image_label: str
    frame_count: int
    risk_score: int
    risk_level: RiskLevel
    detections: list[dict]
    headline: str
    narrative: str


@runtime_checkable
class VisionAnalysisEngine(Protocol):
    provider: str
    model_version: str
    simulated: bool

    def analyze(self, ctx: AnalysisContext) -> AnalysisOutcome: ...

    def info(self) -> dict: ...


def get_engine() -> VisionAnalysisEngine:
    """Resolve the configured engine. Imported lazily to avoid import cycles."""
    provider = settings.AI_PROVIDER
    if provider == "simulated":
        from app.services.ai.simulated import SimulatedVisionEngine

        return SimulatedVisionEngine()

    from app.services.ai.remote import RemoteVisionEngine

    return RemoteVisionEngine(provider=provider)

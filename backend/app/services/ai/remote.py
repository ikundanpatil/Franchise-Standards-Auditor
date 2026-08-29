"""
Real vision-engine adapter — interface only.

This is the single wiring point for a production model. Implement ``analyze`` to
call your provider (an OpenAI / Anthropic vision request, or a RocketRide vision
pipeline via ``client.use({...})``), map its output to ``AnalysisOutcome`` using
``type_code`` values from :mod:`app.services.ai.catalog`, and everything
downstream (violation persistence, report generation, PDF) works unchanged.

Selected by ``AI_PROVIDER=openai|anthropic|rocketride``. Until implemented,
``analyze`` raises ``NotImplementedError`` so misconfiguration fails loudly.
"""

from __future__ import annotations

from app.core.config import settings
from app.services.ai.catalog import VIOLATION_CATALOG
from app.services.ai.engine import AnalysisContext, AnalysisOutcome


class RemoteVisionEngine:
    simulated = False

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.model_version = settings.AI_MODEL_VERSION
        self._api_key = settings.AI_API_KEY
        self._api_base = settings.AI_API_BASE

    def analyze(self, ctx: AnalysisContext) -> AnalysisOutcome:  # noqa: ARG002
        raise NotImplementedError(
            f"AI_PROVIDER={self.provider!r} selected but RemoteVisionEngine.analyze is not "
            "implemented. Wire it to a real model in app/services/ai/remote.py, or set "
            "AI_PROVIDER=simulated."
        )

    def info(self) -> dict:
        return {
            "provider": self.provider,
            "model_version": self.model_version,
            "ready": False,
            "simulated": False,
            "capabilities": [],
            "catalog_size": len(VIOLATION_CATALOG),
            "note": (
                "Interface stub — implement RemoteVisionEngine.analyze and provide "
                "AI_API_KEY to enable."
            ),
        }

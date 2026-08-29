"""
Pluggable vision-analysis engine.

``get_engine()`` returns an implementation of :class:`VisionAnalysisEngine`
chosen by ``settings.AI_PROVIDER``:

* ``simulated`` -> :class:`SimulatedVisionEngine` (default; deterministic mock)
* ``openai`` / ``anthropic`` / ``rocketride`` -> :class:`RemoteVisionEngine`
  (interface only — raises ``NotImplementedError`` until wired)
"""

from app.services.ai.engine import (
    AnalysisContext,
    AnalysisOutcome,
    VisionAnalysisEngine,
    get_engine,
)

__all__ = [
    "AnalysisContext",
    "AnalysisOutcome",
    "VisionAnalysisEngine",
    "get_engine",
]

"""Health-check response."""

from __future__ import annotations

from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    ai_provider: str
    detail: str | None = None

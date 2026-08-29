"""Shared errors, helpers and a status probe for the integration clients."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import AppError


class IntegrationError(AppError):
    """Base for external-integration failures."""

    status_code = 502
    code = "integration_error"


class IntegrationNotConfigured(IntegrationError):
    """A required secret / setting for this integration is missing."""

    status_code = 503
    code = "integration_not_configured"


class IntegrationUpstreamError(IntegrationError):
    """The upstream service returned an error or timed out."""

    status_code = 502
    code = "integration_upstream_error"


def require_config(name: str, **values: Any) -> None:
    """Raise :class:`IntegrationNotConfigured` if any provided value is falsy."""
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise IntegrationNotConfigured(
            f"{name} is not configured — set {', '.join(sorted(missing))} in the environment",
            details={"integration": name, "missing": missing},
        )


def raise_for_upstream(service: str, response: httpx.Response) -> None:
    """Turn a non-2xx upstream response into a clean :class:`IntegrationUpstreamError`."""
    if response.is_success:
        return
    body = response.text[:800]
    raise IntegrationUpstreamError(
        f"{service} returned HTTP {response.status_code}",
        details={"service": service, "status": response.status_code, "body": body},
    )


def integration_status() -> dict[str, Any]:
    """Non-secret snapshot of which integrations are configured (for /ai/integrations)."""
    try:
        from app.integrations.vision_service import get_vision_service

        vision = get_vision_service().status()
    except Exception as exc:  # noqa: BLE001 - status must never raise
        vision = {"backend": settings.VISION_BACKEND, "available": False, "detail": str(exc)}

    return {
        "gemini": {
            "configured": settings.gemini_configured,
            "model": settings.GEMINI_MODEL,
        },
        "supabase": {
            "configured": settings.supabase_configured,
            "url": _host_only(settings.SUPABASE_URL),
            "inspection_bucket": settings.SUPABASE_INSPECTION_BUCKET,
            "reports_table": settings.SUPABASE_REPORTS_TABLE,
        },
        "vision": vision,
    }


def _host_only(url: str | None) -> str | None:
    if not url:
        return None
    try:
        return httpx.URL(url).host
    except Exception:  # noqa: BLE001
        return None

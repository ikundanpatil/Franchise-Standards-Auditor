"""
External-integration clients.

Each module is self-contained, reads its own secrets from ``app.core.config``
(never hardcoded), builds its client lazily, and raises
:class:`IntegrationNotConfigured` when the required env is missing so the API can
answer 503 instead of crashing.

    from app.integrations import gemini_client, supabase_client, vision_service
"""

from app.integrations.base import (
    IntegrationError,
    IntegrationNotConfigured,
    IntegrationUpstreamError,
    integration_status,
)

__all__ = [
    "IntegrationError",
    "IntegrationNotConfigured",
    "IntegrationUpstreamError",
    "integration_status",
]

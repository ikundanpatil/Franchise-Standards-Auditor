"""
Supabase client — inspection-image storage + report persistence.

Uses the Supabase REST surfaces directly via ``httpx``:
  * Storage  : POST /storage/v1/object/{bucket}/{path}
  * PostgREST: POST /rest/v1/{table}

``SUPABASE_URL`` and ``SUPABASE_KEY`` are read from the environment via
``app.core.config`` — never hardcoded. Use a service-role key server-side so
Storage/RLS policies don't block writes.

Public API:
    upload_inspection_image(*, inspection_id, filename, content, content_type=...) -> dict
    save_report(payload) -> dict
"""

from __future__ import annotations

import posixpath
import re
import threading
import uuid
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.base import (
    IntegrationUpstreamError,
    raise_for_upstream,
    require_config,
)

logger = get_logger("app.integrations.supabase")

_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_IMAGE_BYTES = 15 * 1024 * 1024


class SupabaseClient:
    def __init__(self) -> None:
        require_config(
            "Supabase",
            SUPABASE_URL=settings.SUPABASE_URL,
            SUPABASE_KEY=settings.SUPABASE_KEY,
        )
        self._base = (settings.SUPABASE_URL or "").rstrip("/")
        self._key = settings.SUPABASE_KEY or ""
        self._bucket = settings.SUPABASE_INSPECTION_BUCKET
        self._reports_table = settings.SUPABASE_REPORTS_TABLE
        self._client = httpx.Client(
            base_url=self._base,
            timeout=settings.SUPABASE_TIMEOUT_SECONDS,
            headers={
                "apikey": self._key,
                "Authorization": f"Bearer {self._key}",
            },
        )

    # -- storage -------------------------------------------------------
    def upload_inspection_image(
        self,
        *,
        inspection_id: str | uuid.UUID,
        filename: str,
        content: bytes,
        content_type: str = "image/jpeg",
        upsert: bool = True,
    ) -> dict[str, Any]:
        if not content:
            raise IntegrationUpstreamError("Refusing to upload an empty file")
        if len(content) > _MAX_IMAGE_BYTES:
            raise IntegrationUpstreamError(
                f"Image exceeds {_MAX_IMAGE_BYTES // (1024 * 1024)}MB limit"
            )

        segment = _safe_segment(filename) or f"{uuid.uuid4().hex}.jpg"
        path = posixpath.join(str(inspection_id), segment)

        resp = self._client.post(
            f"/storage/v1/object/{self._bucket}/{path}",
            content=content,
            headers={
                "Content-Type": content_type,
                "x-upsert": "true" if upsert else "false",
                "cache-control": "3600",
            },
        )
        raise_for_upstream("Supabase Storage", resp)

        return {
            "bucket": self._bucket,
            "path": path,
            "public_url": f"{self._base}/storage/v1/object/public/{self._bucket}/{path}",
            "size": len(content),
            "content_type": content_type,
        }

    # -- database (PostgREST) ------------------------------------------------
    def save_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(
            f"/rest/v1/{self._reports_table}",
            json=[payload],
            headers={
                "Content-Type": "application/json",
                "Prefer": "return=representation,resolution=merge-duplicates",
            },
        )
        raise_for_upstream("Supabase PostgREST", resp)
        rows = resp.json()
        if isinstance(rows, list) and rows:
            return rows[0]
        return {"inserted": True}

    def fetch_object_bytes(self, url_or_path: str) -> bytes:
        """Download a stored object — accepts a full public URL or a ``bucket/path``."""
        if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
            resp = self._client.get(url_or_path)
        else:
            resp = self._client.get(f"/storage/v1/object/public/{url_or_path.lstrip('/')}")
        raise_for_upstream("Supabase Storage", resp)
        return resp.content

    # -- diagnostics -------------------------------------------------------
    def ping(self) -> bool:
        try:
            resp = self._client.get("/storage/v1/bucket", timeout=5.0)
            return resp.is_success
        except httpx.HTTPError:
            return False


# --- module-level singleton + convenience functions -------------------------
_client: SupabaseClient | None = None
_lock = threading.Lock()


def get_supabase_client() -> SupabaseClient:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = SupabaseClient()
    return _client


def reset_client() -> None:
    global _client
    _client = None


def upload_inspection_image(
    *,
    inspection_id: str | uuid.UUID,
    filename: str,
    content: bytes,
    content_type: str = "image/jpeg",
) -> dict[str, Any]:
    return get_supabase_client().upload_inspection_image(
        inspection_id=inspection_id,
        filename=filename,
        content=content,
        content_type=content_type,
    )


def save_report(payload: dict[str, Any]) -> dict[str, Any]:
    return get_supabase_client().save_report(payload)


def fetch_object_bytes(url_or_path: str) -> bytes:
    return get_supabase_client().fetch_object_bytes(url_or_path)


def _safe_segment(name: str) -> str:
    name = posixpath.basename(name or "").strip()
    return _SAFE_SEGMENT.sub("_", name)[:180]

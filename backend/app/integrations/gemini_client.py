"""
Google Gemini client — complaint analysis + compliance-report narrative.

Talks to the REST ``generateContent`` endpoint directly with ``httpx`` (stable
API, no extra SDK, full timeout/retry control). ``GEMINI_API_KEY`` is read from
the environment via ``app.core.config`` and is never logged or hardcoded.

Public API:
    analyze_complaint(body, *, store_name=None, channel=None) -> dict
    generate_report(*, store_name, risk_score, risk_level, violations, checklist=None) -> dict
"""

from __future__ import annotations

import json
import threading
import time
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.base import (
    IntegrationUpstreamError,
    raise_for_upstream,
    require_config,
)

logger = get_logger("app.integrations.gemini")

_RETRY_STATUSES = {429, 500, 502, 503, 504}


class GeminiClient:
    """Thin wrapper over the Gemini ``generateContent`` REST endpoint."""

    def __init__(self) -> None:
        require_config("Gemini", GEMINI_API_KEY=settings.GEMINI_API_KEY)
        self._api_key = settings.GEMINI_API_KEY or ""
        self._model = settings.GEMINI_MODEL
        self._base = settings.GEMINI_API_BASE.rstrip("/")
        self._client = httpx.Client(timeout=settings.GEMINI_TIMEOUT_SECONDS)

    # -- low level -------------------------------------------------------
    def _generate_json(
        self, *, system: str, prompt: str, temperature: float = 0.2
    ) -> dict[str, Any]:
        url = f"{self._base}/models/{self._model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.post(url, params={"key": self._api_key}, json=payload)
            except httpx.HTTPError as exc:  # timeout / connection
                last_exc = exc
                logger.warning("gemini request failed (attempt %d): %s", attempt + 1, exc)
            else:
                if resp.status_code in _RETRY_STATUSES and attempt < 2:
                    time.sleep(0.6 * (attempt + 1))
                    continue
                raise_for_upstream("Gemini", resp)
                return _extract_json(resp.json())
            time.sleep(0.6 * (attempt + 1))

        raise IntegrationUpstreamError(
            "Gemini request failed after retries", details={"error": str(last_exc)}
        )

    # -- public tasks -------------------------------------------------------
    def analyze_complaint(
        self, body: str, *, store_name: str | None = None, channel: str | None = None
    ) -> dict[str, Any]:
        system = (
            "You are a franchise compliance triage assistant. Classify a customer "
            "complaint about a food-service franchise store. Respond ONLY with JSON "
            'matching this shape: {"severity": "minor|major|critical", '
            '"category": string, "summary": string (<=280 chars), '
            '"urgency": "low|medium|high", "sentiment": "negative|neutral|positive", '
            '"requires_inspection": boolean, "suggested_actions": string[] }.'
        )
        prompt = json.dumps(
            {
                "store": store_name or "unknown",
                "channel": channel or "unknown",
                "complaint": body.strip()[:4000],
            }
        )
        data = self._generate_json(system=system, prompt=prompt)
        return _normalise_complaint(data)

    def generate_report(
        self,
        *,
        store_name: str,
        risk_score: int,
        risk_level: str,
        violations: list[dict[str, Any]],
        checklist: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        system = (
            "You are a franchise standards auditor writing the narrative section of a "
            "compliance report. Be concrete and actionable. Respond ONLY with JSON: "
            '{"headline": string, "summary": string, '
            '"recommendations": [{"title": string, "detail": string, '
            '"priority": "now|soon|monitor", "owner": string}], '
            '"timeline": [{"time": string, "title": string, "detail": string}] }.'
        )
        prompt = json.dumps(
            {
                "store": store_name,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "violations": [
                    {
                        "label": v.get("label"),
                        "category": v.get("category"),
                        "severity": v.get("severity"),
                        "standard_ref": v.get("standard_ref"),
                        "confidence": v.get("confidence"),
                    }
                    for v in violations[:20]
                ],
                "checklist": checklist or [],
            }
        )
        data = self._generate_json(system=system, prompt=prompt, temperature=0.35)
        return _normalise_report(data)


# --- module-level singleton + convenience functions -------------------------
_client: GeminiClient | None = None
_lock = threading.Lock()


def get_gemini_client() -> GeminiClient:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = GeminiClient()
    return _client


def reset_client() -> None:
    """Drop the cached client (tests / config reload)."""
    global _client
    _client = None


def analyze_complaint(
    body: str, *, store_name: str | None = None, channel: str | None = None
) -> dict[str, Any]:
    return get_gemini_client().analyze_complaint(body, store_name=store_name, channel=channel)


def generate_report(
    *,
    store_name: str,
    risk_score: int,
    risk_level: str,
    violations: list[dict[str, Any]],
    checklist: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return get_gemini_client().generate_report(
        store_name=store_name,
        risk_score=risk_score,
        risk_level=risk_level,
        violations=violations,
        checklist=checklist,
    )


# --- response parsing helpers ------------------------------------------------
def _extract_json(response_body: dict[str, Any]) -> dict[str, Any]:
    try:
        text = response_body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise IntegrationUpstreamError(
            "Gemini response had no text content", details={"raw": str(response_body)[:800]}
        ) from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IntegrationUpstreamError(
            "Gemini did not return valid JSON", details={"text": text[:800]}
        ) from exc
    if not isinstance(parsed, dict):
        raise IntegrationUpstreamError("Gemini returned a non-object JSON payload")
    return parsed


_SEVERITY = {"minor", "major", "critical"}
_URGENCY = {"low", "medium", "high"}
_PRIORITY = {"now", "soon", "monitor"}


def _normalise_complaint(data: dict[str, Any]) -> dict[str, Any]:
    severity = str(data.get("severity", "major")).lower()
    urgency = str(data.get("urgency", "medium")).lower()
    actions = data.get("suggested_actions") or []
    return {
        "severity": severity if severity in _SEVERITY else "major",
        "category": str(data.get("category") or "General"),
        "summary": str(data.get("summary") or "").strip()[:500],
        "urgency": urgency if urgency in _URGENCY else "medium",
        "sentiment": str(data.get("sentiment") or "negative").lower(),
        "requires_inspection": bool(data.get("requires_inspection", False)),
        "suggested_actions": [str(a) for a in actions if str(a).strip()][:8],
    }


def _normalise_report(data: dict[str, Any]) -> dict[str, Any]:
    recs = []
    for r in data.get("recommendations") or []:
        if not isinstance(r, dict):
            continue
        priority = str(r.get("priority", "soon")).lower()
        recs.append(
            {
                "title": str(r.get("title") or "").strip(),
                "detail": str(r.get("detail") or "").strip(),
                "priority": priority if priority in _PRIORITY else "soon",
                "owner": str(r.get("owner") or "Store Manager"),
            }
        )
    timeline = [
        {
            "time": str(t.get("time") or ""),
            "title": str(t.get("title") or ""),
            "detail": str(t.get("detail") or ""),
        }
        for t in (data.get("timeline") or [])
        if isinstance(t, dict)
    ]
    return {
        "headline": str(data.get("headline") or "").strip(),
        "summary": str(data.get("summary") or "").strip(),
        "recommendations": recs[:8],
        "timeline": timeline[:12],
    }

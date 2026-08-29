"""
Local YOLO vision service — NO API key.

Runs an Ultralytics YOLO model on-device to detect compliance issues in an
inspection photo and maps each detection onto the shared violation catalogue
(``app.services.ai.catalog``) so the output matches every other producer of
detections in the system.

Enable with ``VISION_BACKEND=yolo`` and install the extras:
    pip install -r requirements-vision.txt
plus a model file at ``YOLO_MODEL_PATH``. A purpose-trained model should expose
classes like ``no_gloves`` / ``dirty_floor`` / ``uncovered_food`` (see
``_LABEL_MAP``); unmapped classes are ignored.

If the package or model is missing, calls raise ``IntegrationNotConfigured`` and
callers may fall back to the simulated engine.
"""

from __future__ import annotations

import io
import threading
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.base import IntegrationNotConfigured, IntegrationUpstreamError
from app.services.ai.catalog import CATALOG_BY_CODE

logger = get_logger("app.integrations.vision")

# YOLO class name (lowercased) -> violation-catalogue code.
_LABEL_MAP: dict[str, str] = {
    "no_gloves": "v-gloves",
    "missing_gloves": "v-gloves",
    "bare_hands": "v-gloves",
    "dirty_floor": "v-floor",
    "wet_floor": "v-floor",
    "expired_label": "v-label",
    "old_label": "v-label",
    "uncovered_food": "v-uncovered",
    "open_food": "v-uncovered",
    "nonstandard_signage": "v-signage",
    "legacy_signage": "v-signage",
    "blocked_handwash": "v-handwash",
    "handwash_blocked": "v-handwash",
    "pest_gap": "v-pest",
    "door_gap": "v-pest",
    "overflow_bin": "v-waste",
    "bin_full": "v-waste",
    "bad_uniform": "v-uniform",
    "no_badge": "v-uniform",
    "cold_hold_high": "v-temp",
    "temp_high": "v-temp",
}


class LocalVisionService:
    """Lazy wrapper around an Ultralytics YOLO model."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._model_names: dict[int, str] = {}
        self._lock = threading.Lock()

    # -- model loading -------------------------------------------------------
    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        with self._lock:
            if self._model is not None:
                return self._model
            try:
                from ultralytics import YOLO
            except ImportError as exc:  # package not installed
                raise IntegrationNotConfigured(
                    "YOLO vision service unavailable — install requirements-vision.txt "
                    "(ultralytics) to enable it",
                    details={"missing": ["ultralytics"]},
                ) from exc

            model_path = settings.YOLO_MODEL_PATH
            # A bare weights name (e.g. yolov8n.pt) is fetched by ultralytics on
            # first use; an explicit path must exist.
            if ("/" in model_path or "\\" in model_path) and not Path(model_path).exists():
                raise IntegrationNotConfigured(
                    f"YOLO model file not found at {model_path!r}",
                    details={"YOLO_MODEL_PATH": model_path},
                )

            logger.info("loading YOLO model: %s", model_path)
            model = YOLO(model_path)
            if settings.YOLO_DEVICE:
                model.to(settings.YOLO_DEVICE)
            self._model = model
            self._model_names = dict(getattr(model, "names", {}) or {})
            return model

    # -- inference -------------------------------------------------------
    def analyze_image(
        self, content: bytes, *, min_confidence: float | None = None
    ) -> list[dict[str, Any]]:
        if not content:
            raise IntegrationUpstreamError("Empty image payload")

        model = self._ensure_model()
        threshold = (
            settings.YOLO_CONFIDENCE_THRESHOLD if min_confidence is None else float(min_confidence)
        )

        try:
            from PIL import Image

            image = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception as exc:  # noqa: BLE001 - any decode failure
            raise IntegrationUpstreamError("Could not decode image bytes") from exc

        try:
            results = model.predict(image, conf=threshold, verbose=False)
        except Exception as exc:  # noqa: BLE001 - inference failure
            raise IntegrationUpstreamError(f"YOLO inference failed: {exc}") from exc

        detections: list[dict[str, Any]] = []
        for result in results:
            names = dict(getattr(result, "names", {}) or self._model_names)
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                raw_name = str(names.get(cls_id, cls_id)).lower()
                code = _LABEL_MAP.get(raw_name)
                if code is None or code not in CATALOG_BY_CODE:
                    continue

                x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0].tolist())
                spec = CATALOG_BY_CODE[code]
                detections.append(
                    {
                        "type_code": spec.code,
                        "label": spec.label,
                        "category": spec.category,
                        "severity": spec.severity.value,
                        "confidence": round(confidence, 3),
                        "bounding_box": [
                            round(min(x1, x2), 4),
                            round(min(y1, y2), 4),
                            round(abs(x2 - x1), 4),
                            round(abs(y2 - y1), 4),
                        ],
                        "explanation": (
                            f"YOLO detected '{raw_name}' at {round(confidence * 100)}% "
                            f"confidence. {spec.rationale.capitalize()}."
                        ),
                        "standard_ref": spec.standard_ref,
                        "remediation": spec.remediation,
                    }
                )
        return detections

    # -- diagnostics (never raises) ------------------------------------------
    def status(self) -> dict[str, Any]:
        info: dict[str, Any] = {
            "backend": "yolo" if settings.VISION_BACKEND == "yolo" else settings.VISION_BACKEND,
            "model_path": settings.YOLO_MODEL_PATH,
            "confidence_threshold": settings.YOLO_CONFIDENCE_THRESHOLD,
            "mapped_classes": sorted(set(_LABEL_MAP)),
        }
        try:
            import ultralytics  # noqa: F401

            info["ultralytics_installed"] = True
        except ImportError:
            info["ultralytics_installed"] = False
        info["available"] = info["ultralytics_installed"] and settings.VISION_BACKEND == "yolo"
        return info


_service: LocalVisionService | None = None
_lock = threading.Lock()


def get_vision_service() -> LocalVisionService:
    global _service
    if _service is None:
        with _lock:
            if _service is None:
                _service = LocalVisionService()
    return _service


def analyze_image(content: bytes, *, min_confidence: float | None = None) -> list[dict[str, Any]]:
    return get_vision_service().analyze_image(content, min_confidence=min_confidence)

"""
Tiny in-process pub/sub for live inspection progress.

``progress_hub.publish(key, event)`` is safe to call from sync worker threads
(the analysis pipeline and background tasks run in the threadpool); it hands the
event to each subscriber's asyncio queue via ``call_soon_threadsafe``.

Single-process only. For multi-worker deployments back this with Redis pub/sub —
the ``publish`` / ``subscribe`` surface stays the same.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from typing import Any, TypedDict

from app.core.logging import get_logger

logger = get_logger("app.realtime")

_QUEUE_MAXSIZE = 200


class ProgressEvent(TypedDict, total=False):
    inspection_id: str
    stage: str  # queued|uploading|detecting|scoring|persisting|complaint|report|done|error
    progress: float  # 0.0 – 1.0
    message: str
    data: dict[str, Any]


class ProgressHub:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        """Called once from the app lifespan so sync publishers can reach the loop."""
        self._loop = loop or asyncio.get_event_loop()

    # -- subscriber side (async) ------------------------------------------------
    async def subscribe(self, key: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=_QUEUE_MAXSIZE)
        self._subscribers[key].add(queue)
        return queue

    def unsubscribe(self, key: str, queue: asyncio.Queue) -> None:
        subs = self._subscribers.get(key)
        if subs:
            subs.discard(queue)
            if not subs:
                self._subscribers.pop(key, None)

    def has_subscribers(self, key: str) -> bool:
        return bool(self._subscribers.get(key))

    # -- publisher side (safe from any thread) --------------------------------
    def publish(self, key: str, event: ProgressEvent) -> None:
        subs = list(self._subscribers.get(key, ()))
        if not subs:
            return
        payload: ProgressEvent = {"inspection_id": key, **event}
        loop = self._loop
        for queue in subs:
            if loop is not None and loop.is_running():
                loop.call_soon_threadsafe(self._safe_put, queue, payload)
            else:  # pragma: no cover - loop not bound (e.g. plain unit test)
                self._safe_put(queue, payload)

    @staticmethod
    def _safe_put(queue: asyncio.Queue, payload: ProgressEvent) -> None:
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(payload)


progress_hub = ProgressHub()

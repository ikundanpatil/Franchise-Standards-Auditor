"""
WebSocket endpoints for live progress.

    /api/v1/ws/inspections/{inspection_id}?token=<access_jwt>
    /api/v1/ws/dashboard?token=<access_jwt>

Auth is via the ``token`` query param (browsers cannot set headers on a
WebSocket handshake). Single-process fan-out — see ``app.realtime.progress``.
"""

from __future__ import annotations

import asyncio
import contextlib
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.logging import get_logger
from app.core.security import TokenError, decode_token
from app.realtime import progress_hub

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = get_logger("app.ws")

_IDLE_TIMEOUT = 300  # seconds with no event before we send a keepalive


def _authorised(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token")
    if not token:
        return False
    try:
        decode_token(token, expected_type="access")
    except TokenError:
        return False
    return True


async def _stream(websocket: WebSocket, key: str) -> None:
    await websocket.accept()
    queue = await progress_hub.subscribe(key)
    await websocket.send_json({"stage": "connected", "key": key})
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=_IDLE_TIMEOUT)
            except TimeoutError:
                await websocket.send_json({"stage": "keepalive"})
                continue
            await websocket.send_json(event)
            if event.get("stage") in ("done", "error"):
                break
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        logger.exception("ws stream error for %s", key)
    finally:
        progress_hub.unsubscribe(key, queue)
        with contextlib.suppress(Exception):
            await websocket.close()


@router.websocket("/inspections/{inspection_id}")
async def inspection_progress(websocket: WebSocket, inspection_id: uuid.UUID) -> None:
    if not _authorised(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await _stream(websocket, str(inspection_id))


@router.websocket("/dashboard")
async def dashboard_updates(websocket: WebSocket) -> None:
    if not _authorised(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    queue = await progress_hub.subscribe("dashboard")
    await websocket.send_json({"stage": "connected", "key": "dashboard"})
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=_IDLE_TIMEOUT)
            except TimeoutError:
                await websocket.send_json({"stage": "keepalive"})
                continue
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        progress_hub.unsubscribe("dashboard", queue)

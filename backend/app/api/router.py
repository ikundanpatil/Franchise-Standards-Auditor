"""The aggregate v1 router — every resource module mounted under one prefix."""

from __future__ import annotations

from fastapi import APIRouter

from app.routers import (
    ai,
    auth,
    complaints,
    dashboard,
    flow,
    inspections,
    reports,
    stores,
    violations,
    ws,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(stores.router)
api_router.include_router(inspections.router)
api_router.include_router(flow.router)
api_router.include_router(violations.router)
api_router.include_router(complaints.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai.router)
api_router.include_router(ws.router)

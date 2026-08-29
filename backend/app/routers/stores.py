"""Stores: CRUD, list filtering, and per-store rollups for Location Memory."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.enums import RiskLevel, StoreStatus, UserRole
from app.schemas.common import Message, Page
from app.schemas.complaint import ComplaintOut
from app.schemas.inspection import InspectionOut
from app.schemas.store import StoreCreate, StoreDetail, StoreHistory, StoreOut, StoreUpdate
from app.services import complaint_service, inspection_service, store_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/stores", tags=["stores"])

ManageStores = require_roles(UserRole.ADMIN, UserRole.AREA_MANAGER)


@router.get("", response_model=Page[StoreOut])
def list_stores(
    user: CurrentUser,
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    q: str | None = Query(None, description="Search name / code / address"),
    region: str | None = None,
    risk_level: RiskLevel | None = None,
    status_: Annotated[StoreStatus | None, Query(alias="status")] = None,
    brand: str | None = None,
) -> Page[StoreOut]:
    return store_service.list_stores(
        db, user, params, q=q, region=region, risk_level=risk_level, status=status_, brand=brand
    )


@router.get("/regions", response_model=list[str])
def list_regions(user: CurrentUser, db: DbSession) -> list[str]:  # noqa: ARG001
    return store_service.distinct_regions(db)


@router.post(
    "",
    response_model=StoreOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ManageStores)],
)
def create_store(payload: StoreCreate, db: DbSession) -> StoreOut:
    return StoreOut.model_validate(store_service.create_store(db, payload))


@router.get("/{store_id}", response_model=StoreDetail)
def get_store(store_id: uuid.UUID, user: CurrentUser, db: DbSession) -> StoreDetail:
    return StoreDetail.model_validate(store_service.get_store(db, store_id, user))


@router.patch("/{store_id}", response_model=StoreOut, dependencies=[Depends(ManageStores)])
def update_store(
    store_id: uuid.UUID, payload: StoreUpdate, user: CurrentUser, db: DbSession
) -> StoreOut:
    store = store_service.get_store(db, store_id, user)
    return StoreOut.model_validate(store_service.update_store(db, store, payload))


@router.delete(
    "/{store_id}",
    response_model=Message,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def delete_store(store_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Message:
    store = store_service.get_store(db, store_id, user)
    store_service.delete_store(db, store)
    return Message(message=f"Store {store.code} deleted")


@router.get("/{store_id}/inspections", response_model=Page[InspectionOut])
def store_inspections(
    store_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
) -> Page[InspectionOut]:
    store_service.get_store(db, store_id, user)  # access check
    return inspection_service.list_inspections(db, user, params, store_id=store_id)


@router.get("/{store_id}/complaints", response_model=Page[ComplaintOut])
def store_complaints(
    store_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
) -> Page[ComplaintOut]:
    store_service.get_store(db, store_id, user)
    return complaint_service.list_complaints(db, params, store_id=store_id)


@router.get("/{store_id}/history", response_model=StoreHistory)
def store_history(
    store_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    days: int = Query(90, ge=7, le=365),
) -> StoreHistory:
    store = store_service.get_store(db, store_id, user)
    return StoreHistory.model_validate(store_service.store_history(db, store, days=days))

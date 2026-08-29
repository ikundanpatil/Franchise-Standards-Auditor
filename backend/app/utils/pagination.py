"""
Offset pagination helpers shared by list endpoints.

``PageParams`` is a FastAPI dependency (``page`` / ``size`` query params);
``paginate`` runs the count + slice and returns a dict that fits ``schemas.common.Page``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any

from fastapi import Query
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

MAX_PAGE_SIZE = 100


@dataclass(slots=True)
class PageParams:
    page: int
    size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


def page_params(
    page: int = Query(1, ge=1, description="1-based page number"),
    size: int = Query(20, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
) -> PageParams:
    return PageParams(page=page, size=size)


def paginate(db: Session, stmt: Select, params: PageParams) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = db.scalars(stmt.offset(params.offset).limit(params.size)).all()
    return {
        "items": list(rows),
        "total": int(total),
        "page": params.page,
        "size": params.size,
        "pages": ceil(total / params.size) if params.size else 0,
    }

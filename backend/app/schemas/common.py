"""Generic response envelopes."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Message(BaseModel):
    """Simple ``{"message": "..."}`` acknowledgement."""

    message: str


class PageMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int


class Page(BaseModel, Generic[T]):
    """Paginated list envelope: ``{items, total, page, size, pages}``."""

    items: list[T]
    total: int = Field(..., description="Total rows matching the query")
    page: int = Field(..., description="1-based page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

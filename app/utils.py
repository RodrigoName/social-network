"""Utility functions for the social-network API.

Provides:
- Pagination helper for SQLAlchemy queries.
- Datetime utilities (UTC now, ISO formatting/parsing).
- Standardized error response generation.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Callable, Iterable, List, Tuple, TypeVar, Union

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query

T = TypeVar("T")

# --------------------------------------------------------------------------- #
# Pagination
# --------------------------------------------------------------------------- #


class PaginationMeta(BaseModel):
    """Metadata returned alongside paginated results."""

    total: int = Field(..., description="Total number of items matching the query.")
    page: int = Field(..., description="Current page number (1‑based).")
    size: int = Field(..., description="Number of items per page.")
    pages: int = Field(..., description="Total number of pages.")


def paginate(
    query: Query,
    *,
    page: int = 1,
    size: int = 10,
    max_size: int = 100,
) -> Tuple[List[T], PaginationMeta]:
    """
    Paginate a SQLAlchemy ``Query`` object.

    Args:
        query: The SQLAlchemy query to paginate.
        page: 1‑based page number (defaults to 1). Must be >= 1.
        size: Number of items per page (defaults to 10). Capped by ``max_size``.
        max_size: Upper bound for ``size`` to avoid excessive payloads.

    Returns:
        A tuple ``(items, meta)`` where ``items`` is a list of model instances
        and ``meta`` is a :class:`PaginationMeta` instance.
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be >= 1.")
    if size < 1:
        raise HTTPException(status_code=400, detail="Page size must be >= 1.")
    size = min(size, max_size)

    total = query.order_by(None).count()  # remove any ORDER BY for efficient count
    pages = (total + size - 1) // size if total else 1
    offset = (page - 1) * size

    items = query.offset(offset).limit(size).all()

    meta = PaginationMeta(total=total, page=page, size=size, pages=pages)
    return items, meta


# --------------------------------------------------------------------------- #
# Datetime utilities
# --------------------------------------------------------------------------- #


def utc_now() -> _dt.datetime:
    """Return the current UTC datetime with timezone information."""
    return _dt.datetime.now(_dt.timezone.utc)


def to_iso(dt: _dt.datetime) -> str:
    """
    Convert a datetime to an ISO‑8601 string in UTC.

    If ``dt`` is naive, it is assumed to be UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc).isoformat()


def parse_iso(value: str) -> _dt.datetime:
    """
    Parse an ISO‑8601 string into a timezone‑aware ``datetime`` (UTC).

    Raises:
        ValueError: If the string cannot be parsed.
    """
    dt = _dt.datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    else:
        dt = dt.astimezone(_dt.timezone.utc)
    return dt


def time_ago(dt: _dt.datetime) -> str:
    """
    Return a human‑readable relative time string (e.g., ``'5 minutes ago'``).

    The input datetime is assumed to be UTC or timezone‑aware.
    """
    now = utc_now()
    delta = now - dt if now > dt else _dt.timedelta(0)

    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''} ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


# --------------------------------------------------------------------------- #
# Error response helpers
# --------------------------------------------------------------------------- #


class ErrorResponse(BaseModel):
    """Standard JSON error payload."""

    code: int = Field(..., description="HTTP status code.")
    detail: str = Field(..., description="Human‑readable error description.")
    timestamp: str = Field(..., description="ISO‑8601 timestamp of the error.")


def error_response(status_code: int, detail: str) -> JSONResponse:
    """
    Build a FastAPI ``JSONResponse`` with a standardized error payload.

    Args:
        status_code: HTTP status code to return.
        detail: Human‑readable description of the error.

    Returns:
        ``JSONResponse`` instance ready to be returned from a route handler.
    """
    payload = ErrorResponse(
        code=status_code,
        detail=detail,
        timestamp=to_iso(utc_now()),
    )
    return JSONResponse(status_code=status_code, content=payload.dict())


def raise_http_error(status_code: int, detail: str) -> None:
    """
    Shortcut to raise a FastAPI ``HTTPException`` with a consistent detail format.

    This function does not return; it always raises.
    """
    raise HTTPException(status_code=status_code, detail=detail)


# --------------------------------------------------------------------------- #
# Miscellaneous helpers
# --------------------------------------------------------------------------- #


def chunked(iterable: Iterable[T], size: int) -> List[List[T]]:
    """
    Split an iterable into chunks of ``size`` elements.

    Useful for batch database operations.

    Args:
        iterable: Any iterable (list, generator, etc.).
        size: Desired chunk size; must be > 0.

    Returns:
        List of lists, each containing up to ``size`` elements.
    """
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0.")
    chunk: List[T] = []
    result: List[List[T]] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            result.append(chunk)
            chunk = []
    if chunk:
        result.append(chunk)
    return result
"""
Portable column types.

``GUID`` stores UUIDs as a 36-char canonical string (``str(uuid.UUID)``) on
every backend — PostgreSQL, SQLite, etc. Application code always sees a
``uuid.UUID``. A single representation keeps migrations identical across the
databases used for tests and production; on PostgreSQL you lose the native
``uuid`` type but gain a migration that needs no dialect branching.
"""

from __future__ import annotations

import uuid

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):  # noqa: ANN001
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):  # noqa: ANN001
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

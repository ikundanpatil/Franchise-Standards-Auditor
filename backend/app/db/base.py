"""
Import surface for Alembic and ``create_all``.

Alembic's ``env.py`` imports ``Base`` from here; importing this module pulls in
every model so ``Base.metadata`` is complete.
"""

from app.db.base_class import Base  # noqa: F401
from app.models import (  # noqa: F401
    AIAnalysis,
    Complaint,
    Inspection,
    Report,
    Store,
    User,
    Violation,
)

__all__ = ["Base"]

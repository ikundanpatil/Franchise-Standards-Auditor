"""
SQLAlchemy models.

Importing this package imports every model, which is what Alembic's
``target_metadata`` and ``Base.metadata.create_all`` rely on.
"""

from app.db.base_class import Base
from app.models.ai_analysis import AIAnalysis
from app.models.complaint import Complaint
from app.models.enums import (
    AIAnalysisStatus,
    ComplaintChannel,
    ComplaintStatus,
    InspectionMethod,
    InspectionSource,
    InspectionStatus,
    ReportStatus,
    RiskLevel,
    Severity,
    StoreStatus,
    UserRole,
    ViolationStatus,
)
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.store import Store
from app.models.user import User
from app.models.violation import Violation

__all__ = [
    "Base",
    "User",
    "Store",
    "Inspection",
    "Violation",
    "Complaint",
    "Report",
    "AIAnalysis",
    "UserRole",
    "RiskLevel",
    "Severity",
    "StoreStatus",
    "InspectionStatus",
    "InspectionMethod",
    "InspectionSource",
    "ViolationStatus",
    "ComplaintStatus",
    "ComplaintChannel",
    "ReportStatus",
    "AIAnalysisStatus",
]

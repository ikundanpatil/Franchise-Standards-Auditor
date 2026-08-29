"""
Enumerations shared by models and schemas.

All are ``str`` enums so they serialise as their value in JSON and store as
VARCHAR in the database (``Enum(..., native_enum=False)`` in the models) — this
keeps migrations portable and avoids PostgreSQL ``ALTER TYPE`` friction.
"""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    AREA_MANAGER = "area_manager"
    INSPECTOR = "inspector"
    FRANCHISE_OWNER = "franchise_owner"

    @property
    def label(self) -> str:
        return {
            UserRole.ADMIN: "Admin",
            UserRole.AREA_MANAGER: "Area Manager",
            UserRole.INSPECTOR: "Inspector",
            UserRole.FRANCHISE_OWNER: "Franchise Owner",
        }[self]


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class StoreStatus(str, Enum):
    ACTIVE = "active"
    ONBOARDING = "onboarding"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class InspectionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InspectionMethod(str, Enum):
    AI_PHOTO = "ai_photo"
    AI_VIDEO = "ai_video"
    ON_SITE = "on_site"


class InspectionSource(str, Enum):
    SCHEDULED = "scheduled"
    AD_HOC = "ad_hoc"
    COMPLAINT_FOLLOWUP = "complaint_followup"
    REINSPECTION = "reinspection"


class ViolationStatus(str, Enum):
    OPEN = "open"
    IN_REMEDIATION = "in_remediation"
    RESOLVED = "resolved"
    WAIVED = "waived"


class ComplaintStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ComplaintChannel(str, Enum):
    APP = "app"
    PHONE = "phone"
    EMAIL = "email"
    WALK_IN = "walk_in"
    SOCIAL = "social"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    FINAL = "final"


class AIAnalysisStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

"""
Seed the database with demo data.

    python -m app.db.seed              # create if missing (safe to re-run)
    python -m app.db.seed --fresh      # DROP ALL TABLES, recreate, then seed

Creates: one admin (from FIRST_ADMIN_* env), one user per role, the 15 demo
stores from the frontend, and a spread of completed inspections + AI analyses +
violations + reports produced by the real analysis pipeline.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from sqlalchemy import func, select

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine, session_scope
from app.models.complaint import Complaint
from app.models.enums import (
    ComplaintChannel,
    InspectionMethod,
    InspectionSource,
    InspectionStatus,
    RiskLevel,
    Severity,
    StoreStatus,
    UserRole,
)
from app.models.inspection import Inspection
from app.models.store import Store
from app.models.user import User
from app.schemas.ai import AnalyzeRequest
from app.services import ai_service, report_service
from app.utils.datetime import utcnow

logger = get_logger("app.seed")

# 15 demo stores — mirrors apps/franchiseguard-ai-ui/src/data/stores.ts
STORES: list[dict] = [
    {
        "code": "#201",
        "name": "StarBrew Cafe",
        "region": "Midtown",
        "address": "412 Marlowe Ave, Midtown",
        "risk": RiskLevel.LOW,
        "score": 96,
        "tags": ["Flagship", "Drive-thru"],
    },
    {
        "code": "#204",
        "name": "Pizza Planet",
        "region": "Riverside",
        "address": "77 Riverside Plaza, Dock 4",
        "risk": RiskLevel.HIGH,
        "score": 64,
        "tags": ["Watch list", "High footfall"],
    },
    {
        "code": "#087",
        "name": "FreshBowl Kitchen",
        "region": "Downtown",
        "address": "9 Congress St, Downtown Center",
        "risk": RiskLevel.MEDIUM,
        "score": 79,
        "tags": ["Mall unit"],
    },
    {
        "code": "#133",
        "name": "Burger Hub",
        "region": "Airport",
        "address": "Terminal C, Gate 22, Airport",
        "risk": RiskLevel.CRITICAL,
        "score": 58,
        "tags": ["Escalated", "24/7"],
    },
    {
        "code": "#045",
        "name": "Urban Coffee",
        "region": "Midtown",
        "address": "220 Lexington Row, Midtown",
        "risk": RiskLevel.LOW,
        "score": 91,
        "tags": ["Kiosk"],
    },
    {
        "code": "#118",
        "name": "Green Fork Deli",
        "region": "Harbor",
        "address": "3 Wharf Lane, Harbor District",
        "risk": RiskLevel.MEDIUM,
        "score": 83,
        "tags": ["Seasonal patio"],
    },
    {
        "code": "#160",
        "name": "Noodle Bar 9",
        "region": "Downtown",
        "address": "150 Canal St, Downtown",
        "risk": RiskLevel.LOW,
        "score": 88,
        "tags": ["Late night"],
    },
    {
        "code": "#092",
        "name": "The Roasted Bean",
        "region": "Westside",
        "address": "61 Sunset Blvd, Westside",
        "risk": RiskLevel.HIGH,
        "score": 72,
        "tags": ["New franchisee"],
    },
    {
        "code": "#210",
        "name": "Taco Junction",
        "region": "Riverside",
        "address": "500 Esplanade, Riverside",
        "risk": RiskLevel.LOW,
        "score": 90,
        "tags": ["Drive-thru"],
    },
    {
        "code": "#076",
        "name": "Bagel & Co.",
        "region": "Harbor",
        "address": "18 Pier Approach, Harbor",
        "risk": RiskLevel.MEDIUM,
        "score": 85,
        "tags": ["Breakfast only"],
    },
    {
        "code": "#141",
        "name": "Wok This Way",
        "region": "Airport",
        "address": "Terminal A, Food Court, Airport",
        "risk": RiskLevel.HIGH,
        "score": 68,
        "tags": ["High footfall"],
    },
    {
        "code": "#058",
        "name": "Sunrise Diner",
        "region": "Westside",
        "address": "900 Palm Ave, Westside",
        "risk": RiskLevel.LOW,
        "score": 93,
        "tags": ["Family"],
    },
    {
        "code": "#167",
        "name": "Curry Leaf Express",
        "region": "Downtown",
        "address": "44 Market Sq, Downtown",
        "risk": RiskLevel.MEDIUM,
        "score": 81,
        "tags": ["Delivery hub"],
    },
    {
        "code": "#103",
        "name": "Smoothie Yard",
        "region": "Midtown",
        "address": "77 Garden Terrace, Midtown",
        "risk": RiskLevel.LOW,
        "score": 94,
        "tags": ["Kiosk", "Seasonal"],
    },
    {
        "code": "#189",
        "name": "Grill House 12",
        "region": "Harbor",
        "address": "12 Lighthouse Rd, Harbor",
        "risk": RiskLevel.MEDIUM,
        "score": 76,
        "tags": ["Waterfront"],
    },
]

USERS: list[dict] = [
    {
        "email": "priya.nair@franchiseguard.ai",
        "name": "Priya Nair",
        "role": UserRole.AREA_MANAGER,
        "region": "Midtown",
    },
    {
        "email": "d.okafor@franchiseguard.ai",
        "name": "Dara Okafor",
        "role": UserRole.INSPECTOR,
        "region": "Midtown",
    },
    {
        "email": "m.halloran@franchiseguard.ai",
        "name": "Mia Halloran",
        "role": UserRole.FRANCHISE_OWNER,
        "region": "Riverside",
    },
]

_CHECKLIST = [
    {"area": "Kitchen Cleanliness", "ok": True, "note": None},
    {"area": "Staff Hygiene", "ok": False, "note": "Glove use inconsistent on the line"},
    {"area": "Food Storage", "ok": True, "note": None},
    {"area": "Branding Compliance", "ok": True, "note": None},
    {"area": "Pest Control", "ok": True, "note": None},
]


def _get_or_create_user(
    db, *, email: str, name: str, role: UserRole, password: str, region=None
) -> User:
    user = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user:
        return user
    user = User(
        email=email.lower(),
        full_name=name,
        hashed_password=hash_password(password),
        role=role,
        region=region,
        is_active=True,
    )
    db.add(user)
    db.flush()
    logger.info("created user %s (%s)", email, role.value)
    return user


def seed(fresh: bool = False) -> None:
    configure_logging()
    if fresh:
        logger.warning("--fresh: dropping and recreating all tables")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with session_scope() as db:
        admin = _get_or_create_user(
            db,
            email=settings.FIRST_ADMIN_EMAIL,
            name=settings.FIRST_ADMIN_NAME,
            role=UserRole.ADMIN,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
        staff = [
            _get_or_create_user(
                db,
                email=u["email"],
                name=u["name"],
                role=u["role"],
                password="Demo1234!",
                region=u.get("region"),
            )
            for u in USERS
        ]
        area_manager = next(u for u in staff if u.role == UserRole.AREA_MANAGER)
        inspector = next(u for u in staff if u.role == UserRole.INSPECTOR)
        owner = next(u for u in staff if u.role == UserRole.FRANCHISE_OWNER)

        existing_codes = set(db.scalars(select(Store.code)))
        stores: list[Store] = []
        for spec in STORES:
            if spec["code"] in existing_codes:
                stores.append(db.scalar(select(Store).where(Store.code == spec["code"])))
                continue
            store = Store(
                code=spec["code"],
                name=spec["name"],
                brand="FranchiseGuard",
                region=spec["region"],
                address=spec["address"],
                city=spec["region"],
                country="US",
                status=StoreStatus.ACTIVE,
                risk_level=spec["risk"],
                compliance_score=spec["score"],
                opened_on=date(2023, 1, 1) + timedelta(days=hash(spec["code"]) % 500),
                next_inspection_due=date.today() + timedelta(days=14),
                manager_id=area_manager.id,
                owner_id=owner.id if spec["region"] == "Riverside" else None,
                tags=spec["tags"],
            )
            db.add(store)
            stores.append(store)
        db.flush()

        # A few complaints.
        if db.scalar(select(func.count(Complaint.id))) == 0:
            for store in stores[:5]:
                db.add(
                    Complaint(
                        store_id=store.id,
                        channel=ComplaintChannel.APP,
                        severity=Severity.MAJOR
                        if store.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
                        else Severity.MINOR,
                        subject="Cleanliness concern",
                        body=f"Customer reported sticky tables and an untidy service area at {store.name}.",
                        reporter_name="Anonymous",
                        received_at=utcnow() - timedelta(days=hash(store.code) % 20 + 1),
                    )
                )
        db.flush()

        # Completed inspections + analyses + reports for the riskier half.
        already = db.scalar(select(func.count(Inspection.id))) or 0
        if already == 0:
            targets = sorted(stores, key=lambda s: s.compliance_score)[:6]
            for i, store in enumerate(targets):
                inspection = Inspection(
                    store_id=store.id,
                    inspector_id=inspector.id,
                    method=InspectionMethod.AI_PHOTO,
                    source=InspectionSource.SCHEDULED,
                    status=InspectionStatus.IN_PROGRESS,
                    scheduled_for=utcnow() - timedelta(days=i + 1),
                    started_at=utcnow() - timedelta(days=i + 1),
                    checklist=_CHECKLIST,
                    image_label="Kitchen line · station 2",
                    frame_count=2,
                )
                db.add(inspection)
                db.flush()

                analysis = ai_service.run_analysis(
                    db,
                    AnalyzeRequest(
                        inspection_id=inspection.id, persist_violations=True, seed=100 + i
                    ),
                    admin,
                )
                db.refresh(inspection)
                report_service.generate_report(db, inspection, area_manager, finalize=(i % 2 == 0))
                logger.info(
                    "seeded inspection for %s — %s detections",
                    store.code,
                    len(analysis.detections),
                )

        logger.info("seed complete")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the FranchiseGuard database")
    parser.add_argument("--fresh", action="store_true", help="drop & recreate all tables first")
    args = parser.parse_args()
    seed(fresh=args.fresh)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""
Pytest fixtures.

A throwaway SQLite database is configured *before* the app package is imported
(settings are read once at import time). Each test gets a clean schema.
"""

from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./_test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-definitely-long-enough-1234")
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("AI_SIMULATED_LATENCY_MS", "0")
os.environ.setdefault("FIRST_ADMIN_EMAIL", "admin@test.io")
os.environ.setdefault("FIRST_ADMIN_PASSWORD", "AdminPass123!")

import pathlib  # noqa: E402
from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402

_TEST_DB = pathlib.Path("_test.db")


@pytest.fixture(autouse=True)
def _fresh_schema() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _cleanup_db_file() -> Iterator[None]:
    yield
    engine.dispose()
    _TEST_DB.unlink(missing_ok=True)


@pytest.fixture
def db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


# --- user + auth helpers -------------------------------------------------------
def _make_user(db: Session, email: str, role: UserRole, password: str = "Passw0rd!") -> User:
    user = User(
        email=email,
        full_name=email.split("@")[0].title(),
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin(db: Session) -> User:
    return _make_user(db, "admin@test.io", UserRole.ADMIN)


@pytest.fixture
def area_manager(db: Session) -> User:
    return _make_user(db, "am@test.io", UserRole.AREA_MANAGER)


@pytest.fixture
def inspector(db: Session) -> User:
    return _make_user(db, "inspector@test.io", UserRole.INSPECTOR)


def auth_headers(client: TestClient, email: str, password: str = "Passw0rd!") -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def admin_headers(client: TestClient, admin: User) -> dict[str, str]:
    return auth_headers(client, admin.email)


@pytest.fixture
def manager_headers(client: TestClient, area_manager: User) -> dict[str, str]:
    return auth_headers(client, area_manager.email)


@pytest.fixture
def inspector_headers(client: TestClient, inspector: User) -> dict[str, str]:
    return auth_headers(client, inspector.email)

"""
Application configuration.

All settings come from environment variables (12-factor); a local ``.env`` file
is loaded automatically when present. Nothing here is host-specific — the same
image runs locally, on a VM, or on a container platform, differing only by env.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -- App ---------------------------------------------------------------
    PROJECT_NAME: str = "FranchiseGuard AI API"
    DESCRIPTION: str = (
        "Backend for FranchiseGuard AI — franchise standards auditing (PS-18). "
        "Stores, inspections, violations, complaints, compliance reports and a "
        "pluggable AI analysis engine."
    )
    VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # -- Logging ---------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # -- Database ---------------------------------------------------------------
    DATABASE_URL: str = (
        "postgresql+psycopg2://franchiseguard:franchiseguard@localhost:5432/franchiseguard"
    )
    DATABASE_USE_NULL_POOL: bool = False
    DATABASE_ECHO: bool = False
    AUTO_CREATE_TABLES: bool = False

    # -- Auth / JWT ---------------------------------------------------------------
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    FIRST_ADMIN_EMAIL: str = "admin@franchiseguard.ai"
    FIRST_ADMIN_PASSWORD: str = "ChangeMe123!"
    FIRST_ADMIN_NAME: str = "FranchiseGuard Admin"

    # -- CORS ---------------------------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # -- AI engine ---------------------------------------------------------------
    AI_PROVIDER: Literal["simulated", "openai", "anthropic", "rocketride"] = "simulated"
    AI_MODEL_VERSION: str = "fg-vision-2.4"
    AI_SIMULATED_LATENCY_MS: int = 350
    AI_API_KEY: str | None = None
    AI_API_BASE: str | None = None

    # -- RocketRide bridge (not wired yet) --------------------------------------
    ROCKETRIDE_JWKS_URL: str | None = None
    ROCKETRIDE_AUDIENCE: str | None = None

    # -- External integrations (app/integrations/) ----------------------------
    # Google Gemini — complaint analysis + report narrative generation.
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_TIMEOUT_SECONDS: float = 30.0

    # Supabase — inspection-image storage + report persistence.
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_INSPECTION_BUCKET: str = "inspection-images"
    SUPABASE_REPORTS_TABLE: str = "reports"
    SUPABASE_TIMEOUT_SECONDS: float = 30.0

    # YOLO — local vision service, NO API key. Requires `ultralytics` installed
    # (pip install -r requirements-vision.txt) and a model file on disk.
    VISION_BACKEND: Literal["simulated", "yolo"] = "simulated"
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35
    YOLO_DEVICE: str | None = None  # e.g. "cpu", "cuda:0"; None = auto

    @property
    def gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)

    # ---------------------------------------------------------------------
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        """Accept a comma-separated string or a JSON/list value for CORS origins."""
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalise_db_url(cls, value: str) -> str:
        """Coerce bare ``postgres://`` / ``postgresql://`` to the psycopg2 driver."""
        if value.startswith("postgres://"):
            value = "postgresql+psycopg2://" + value[len("postgres://") :]
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg2://" + value[len("postgresql://") :]
        return value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return self.DATABASE_URL

    def assert_production_safe(self) -> None:
        """Fail fast on obviously-insecure production configuration."""
        if not self.is_production:
            return
        problems: list[str] = []
        if len(self.SECRET_KEY) < 32:
            problems.append("SECRET_KEY is too short")
        if self.DEBUG:
            problems.append("DEBUG must be false in production")
        if self.FIRST_ADMIN_PASSWORD == "ChangeMe123!":
            problems.append("FIRST_ADMIN_PASSWORD is still the default")
        if problems:
            raise RuntimeError("Unsafe production configuration: " + "; ".join(problems))

    # Best-effort validation of the DSN shape without blocking non-postgres test URLs.
    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_dsn(cls, value: str) -> str:
        if value.startswith("postgresql"):
            PostgresDsn(value.replace("+psycopg2", ""))
        return value


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so the environment is parsed exactly once per process."""
    return Settings()


settings = get_settings()

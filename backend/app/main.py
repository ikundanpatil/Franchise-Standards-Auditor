"""
FastAPI application entrypoint.

``uvicorn app.main:app`` in production; ``python -m app.main`` for a dev server.
The app is built by :func:`create_app` so tests can construct isolated instances.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse
from sqlalchemy import text

from app import __version__
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.session import engine
from app.middleware.logging import RequestLoggingMiddleware
from app.schemas.health import HealthCheck

logger = get_logger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings.assert_production_safe()
    logger.info(
        "starting %s v%s (env=%s, ai=%s)",
        settings.PROJECT_NAME,
        __version__,
        settings.ENVIRONMENT,
        settings.AI_PROVIDER,
    )

    if settings.AUTO_CREATE_TABLES:
        from app.db.base import Base

        Base.metadata.create_all(bind=engine)
        logger.warning("AUTO_CREATE_TABLES is on — schema created from models, not Alembic")

    yield
    logger.info("shutting down")


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=__version__,
        default_response_class=ORJSONResponse,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
        contact={"name": "FranchiseGuard AI", "url": "https://staging.rocketride.ai"},
        license_info={"name": "MIT"},
    )

    # CORS — browsers calling the API from the RocketRide app / local dev.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-ms"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    @app.get("/health", response_model=HealthCheck, tags=["meta"])
    def health() -> HealthCheck:
        """Liveness + database connectivity probe."""
        db_ok = True
        db_error: str | None = None
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as exc:  # noqa: BLE001
            db_ok = False
            db_error = str(exc)
            logger.error("health check: database unreachable: %s", exc)

        return HealthCheck(
            status="ok" if db_ok else "degraded",
            version=__version__,
            environment=settings.ENVIRONMENT,
            database="ok" if db_ok else "error",
            ai_provider=settings.AI_PROVIDER,
            detail=db_error,
        )

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # noqa: S104 - intended for containers
        port=8000,
        reload=settings.DEBUG,
        log_config=None,
    )

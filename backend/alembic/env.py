"""Alembic migration environment — wired to the app's settings and metadata."""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import settings
from app.db.base import Base  # imports every model -> full metadata

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")


def render_item(type_, obj, autogen_context):  # noqa: ANN001, ARG001
    """Render the portable ``GUID`` type as plain ``sa.String(36)`` in migrations."""
    from app.db.types import GUID

    if type_ == "type" and isinstance(obj, GUID):
        return "sa.String(length=36)"
    return False


def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):  # noqa: ANN001, ARG001
    """``GUID`` reflects as VARCHAR(36); treat that as equivalent (no spurious diff)."""
    from sqlalchemy import String

    from app.db.types import GUID

    if isinstance(metadata_type, GUID) and isinstance(inspected_type, String):
        return False
    return None  # fall back to Alembic's default comparison


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=compare_type,
        compare_server_default=True,
        render_as_batch=_IS_SQLITE,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=compare_type,
            compare_server_default=True,
            render_as_batch=_IS_SQLITE,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

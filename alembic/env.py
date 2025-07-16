import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel

from alembic import context

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
import app.models  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def _get_sync_url() -> str:
    raw = os.getenv("DATABASE_URL")
    if not raw:
        raise RuntimeError("DATABASE_URL isn’t set in environment")
    if raw.startswith("postgresql+asyncpg://"):
        return raw.replace("postgresql+asyncpg://", "postgresql://", 1)
    return raw


def run_migrations_offline():
    url = _get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    url = _get_sync_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

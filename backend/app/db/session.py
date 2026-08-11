import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_engine():
    """Use the configured PostgreSQL database. If it is unreachable (e.g. the
    Docker services are not running during local development), fall back to a
    local SQLite file so request history and analytics still function."""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3} if settings.DATABASE_URL.startswith("postgresql") else {},
    )
    try:
        with engine.connect():
            pass
        logger.info("Connected to configured database.")
        return engine, False
    except Exception as exc:
        logger.warning(
            "Configured database unavailable (%s). Falling back to local SQLite "
            "file for request history. Start docker-compose for PostgreSQL.",
            exc.__class__.__name__,
        )
        sqlite_engine = create_engine(
            "sqlite:///./smartllm_local.db",
            connect_args={"check_same_thread": False},
        )
        return sqlite_engine, True


engine, using_sqlite_fallback = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create the tables SmartLLM needs. On the SQLite fallback we only create
    dialect-agnostic tables (request_logs); the users table uses a PostgreSQL
    UUID type and is managed by the existing Postgres setup."""
    from app.models.base import Base
    from app.models.request_log import RequestLog

    try:
        if using_sqlite_fallback:
            Base.metadata.create_all(bind=engine, tables=[RequestLog.__table__])
        else:
            from app.models.user import User  # noqa: F401 - register model
            Base.metadata.create_all(bind=engine)
    except Exception:
        logger.exception("Failed to initialize database tables.")

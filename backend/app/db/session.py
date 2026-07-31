from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings


def create_database_engine(database_url: str | None = None) -> Engine:
    return create_engine(database_url or get_settings().database_url, pool_pre_ping=True)


_engine: Engine | None = None
_session_local: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def get_session_local() -> sessionmaker[Session]:
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)
    return _session_local


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_local()()
    try:
        yield session
    finally:
        session.close()

"""Conexão com o Postgres."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import config

_engine: Engine | None = None


def engine() -> Engine:
    global _engine
    if _engine is None:
        config.validate()
        _engine = create_engine(config.database_url, pool_pre_ping=True)
    return _engine


@contextmanager
def connection():
    """Context manager transacional. Commit automático ao sair sem erro."""
    with engine().begin() as conn:
        yield conn

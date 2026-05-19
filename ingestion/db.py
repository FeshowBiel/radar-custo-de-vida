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
        # executemany_mode="values_plus_batch" faz o psycopg2 agrupar
        # múltiplas linhas por round-trip (execute_batch). Essencial para
        # upserts contra um Postgres remoto (Neon) — sem isso, séries
        # diárias como a Selic (~7k linhas) levam dezenas de minutos e
        # estouram o timeout do GitHub Actions.
        _engine = create_engine(
            config.database_url,
            pool_pre_ping=True,
            executemany_mode="values_plus_batch",
        )
    return _engine


@contextmanager
def connection():
    """Context manager transacional. Commit automático ao sair sem erro."""
    with engine().begin() as conn:
        yield conn

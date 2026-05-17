"""Acesso a dados para o dashboard, com cache do Streamlit."""
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# .env fica na raiz do projeto (dois níveis acima deste arquivo:
# dashboard/lib/queries.py -> projeto/). Resolvido por caminho absoluto
# para funcionar independente do CWD com que o Streamlit foi iniciado.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _PROJECT_ROOT / ".env"


def _database_url() -> str:
    # Precedência: variável de ambiente / .env (local) -> st.secrets (Streamlit Cloud).
    # Checamos .env primeiro de propósito: acessar st.secrets["..."] sem um
    # secrets.toml faz o Streamlit renderizar caixas de erro na página, mesmo
    # que o Python capture a exceção. No deploy não há .env, então cai no secrets.
    from dotenv import load_dotenv

    if _ENV_PATH.exists():
        load_dotenv(_ENV_PATH)
    else:
        load_dotenv()

    url = os.environ.get("DATABASE_URL", "")
    if url:
        return url

    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        raise RuntimeError(  # noqa: B904
            "DATABASE_URL não definida. Verifique .env ou st.secrets."
        )


@st.cache_resource
def get_engine():
    return create_engine(_database_url(), pool_pre_ping=True)


@st.cache_data(ttl=3600)
def query(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, get_engine())


def inflacao_por_categoria() -> pd.DataFrame:
    return query("SELECT * FROM marts.mart_inflacao_por_categoria ORDER BY ano")


def poder_de_compra() -> pd.DataFrame:
    return query("SELECT * FROM marts.mart_poder_compra_salario ORDER BY data_referencia")


def previsao_ipca() -> pd.DataFrame:
    return query("SELECT * FROM marts.previsao_ipca_raw ORDER BY data_referencia")


def inflacao_regional() -> pd.DataFrame:
    return query("SELECT * FROM marts.mart_inflacao_regional ORDER BY ano")


def ipca_acumulado_12m() -> pd.DataFrame:
    return query(
        "SELECT * FROM staging.int_ipca_acumulado_12m "
        "WHERE ipca_acumulado_12m IS NOT NULL ORDER BY data_referencia"
    )


def ipca_mensal() -> pd.DataFrame:
    return query(
        "SELECT data_referencia, valor FROM raw.bcb_series "
        "WHERE codigo_serie = 433 ORDER BY data_referencia"
    )


def previsao_metadata() -> pd.DataFrame:
    return query(
        "SELECT metricas, gerado_em FROM marts.previsao_metadata ORDER BY gerado_em DESC LIMIT 1"
    )

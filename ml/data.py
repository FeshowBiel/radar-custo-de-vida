"""Carregamento de dados para o módulo de ML."""
import pandas as pd

from ingestion.db import engine


def carregar_ipca_mensal() -> pd.DataFrame:
    """Retorna DataFrame com colunas ['data_referencia', 'valor'] do IPCA mensal."""
    df = pd.read_sql(
        """
        select data_referencia, valor
        from raw.bcb_series
        where codigo_serie = 433
        order by data_referencia
        """,
        engine(),
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"])
    return df.dropna().reset_index(drop=True)

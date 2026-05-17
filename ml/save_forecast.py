"""Gera a previsão, roda o backtest e persiste tudo em marts.previsao_ipca_raw."""
import json
import logging

import pandas as pd
from sqlalchemy import text

from ingestion.db import connection
from ingestion.logging_config import setup_logging
from ml.backtest import backtest
from ml.data import carregar_ipca_mensal
from ml.forecast import prever

logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS marts.previsao_ipca_raw (
    data_referencia DATE PRIMARY KEY,
    tipo            VARCHAR(12) NOT NULL,
    valor           NUMERIC(18,6),
    limite_inferior NUMERIC(18,6),
    limite_superior NUMERIC(18,6)
);
CREATE TABLE IF NOT EXISTS marts.previsao_metadata (
    id          SERIAL PRIMARY KEY,
    gerado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metricas    JSONB
);
"""


def run(meses: int = 12) -> dict:
    setup_logging()

    df = carregar_ipca_mensal()
    logger.info("Série IPCA carregada: %d meses", len(df))

    metricas = backtest(df, prever, horizonte=12)
    logger.info("Backtest: %s", metricas)

    previsao = prever(df, meses=meses)

    historico = df.assign(
        tipo="historico",
        limite_inferior=pd.Series(dtype="float64"),
        limite_superior=pd.Series(dtype="float64"),
    )
    previsto = previsao.assign(tipo="previsto")

    completo = pd.concat(
        [
            historico[["data_referencia", "tipo", "valor", "limite_inferior", "limite_superior"]],
            previsto[["data_referencia", "tipo", "valor", "limite_inferior", "limite_superior"]],
        ],
        ignore_index=True,
    )
    completo["data_referencia"] = pd.to_datetime(completo["data_referencia"]).dt.date

    with connection() as conn:
        for stmt in DDL.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        conn.execute(text("TRUNCATE marts.previsao_ipca_raw"))
        conn.execute(
            text("""
                INSERT INTO marts.previsao_ipca_raw
                    (data_referencia, tipo, valor, limite_inferior, limite_superior)
                VALUES
                    (:data_referencia, :tipo, :valor, :limite_inferior, :limite_superior)
            """),
            completo.to_dict(orient="records"),
        )
        conn.execute(
            text("INSERT INTO marts.previsao_metadata (metricas) VALUES (:m)"),
            {"m": json.dumps(metricas)},
        )

    logger.info("Previsão persistida: %d linhas", len(completo))
    return metricas


if __name__ == "__main__":
    run()

"""Job: coleta todas as séries do catálogo BCB e faz upsert em raw.bcb_series.

Séries com código inválido são logadas e puladas — o job não aborta.
"""
import logging
from datetime import datetime

from sqlalchemy import text

from ..bcb_client import BCBClient, BCBSeriesError
from ..config import config
from ..db import connection
from ..logging_config import setup_logging
from ..series_catalog import CATALOGO_BCB, SerieBCB

logger = logging.getLogger(__name__)

UPSERT_SQL = text("""
    INSERT INTO raw.bcb_series
        (codigo_serie, nome_serie, categoria, unidade, data_referencia, valor)
    VALUES
        (:codigo_serie, :nome_serie, :categoria, :unidade, :data_referencia, :valor)
    ON CONFLICT (codigo_serie, data_referencia)
    DO UPDATE SET valor = EXCLUDED.valor, coletado_em = NOW()
""")


def _parse_data(s: str):
    return datetime.strptime(s, "%d/%m/%Y").date()


def _parse_valor(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _ingerir_serie(client: BCBClient, serie: SerieBCB) -> int:
    dados = client.get_serie(serie.codigo, inicio=config.historico_inicio)
    rows = [
        {
            "codigo_serie": serie.codigo,
            "nome_serie": serie.nome,
            "categoria": serie.categoria,
            "unidade": serie.unidade,
            "data_referencia": _parse_data(d["data"]),
            "valor": _parse_valor(d["valor"]),
        }
        for d in dados
        if "data" in d
    ]
    if rows:
        with connection() as conn:
            conn.execute(UPSERT_SQL, rows)
    return len(rows)


def run() -> dict:
    """Executa a ingestão. Retorna resumo {nome_serie: n_registros|'FALHOU'}."""
    setup_logging()
    resumo: dict[str, object] = {}

    with BCBClient() as client:
        for serie in CATALOGO_BCB:
            try:
                n = _ingerir_serie(client, serie)
                resumo[serie.nome] = n
                logger.info("OK   %-35s %d registros", serie.nome, n)
            except (BCBSeriesError, Exception) as e:  # noqa: BLE001
                resumo[serie.nome] = "FALHOU"
                logger.warning(
                    "FALHA %-35s código %d: %s",
                    serie.nome,
                    serie.codigo,
                    e,
                )

    ok = sum(1 for v in resumo.values() if isinstance(v, int))
    logger.info("Ingestão BCB concluída: %d/%d séries com dados", ok, len(resumo))
    return resumo


if __name__ == "__main__":
    run()

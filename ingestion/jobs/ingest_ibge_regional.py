"""Job: coleta IPCA regional do IBGE e faz upsert em raw.ibge_ipca_regional."""
import logging

from sqlalchemy import text

from ..db import connection
from ..ibge_client import IBGEClient
from ..logging_config import setup_logging

logger = logging.getLogger(__name__)

UPSERT_SQL = text("""
    INSERT INTO raw.ibge_ipca_regional
        (codigo_localidade, nome_localidade, data_referencia, variavel, valor, raw_payload)
    VALUES
        (:codigo_localidade, :nome_localidade, :data_referencia,
         :variavel, :valor, :raw_payload)
    ON CONFLICT (codigo_localidade, data_referencia, variavel)
    DO UPDATE SET
        valor       = EXCLUDED.valor,
        raw_payload = EXCLUDED.raw_payload,
        coletado_em = NOW()
""")


def run() -> int:
    """Coleta e persiste dados regionais do IBGE. Retorna número de registros."""
    setup_logging()

    with IBGEClient() as client:
        rows = client.get_ipca_regional()

    if not rows:
        logger.warning("IBGE: nenhum dado coletado. Tabela ibge_ipca_regional permanece intacta.")
        return 0

    import json

    for r in rows:
        r["raw_payload"] = json.dumps(r["raw_payload"])

    with connection() as conn:
        conn.execute(UPSERT_SQL, rows)

    logger.info("IBGE: %d registros inseridos/atualizados em raw.ibge_ipca_regional", len(rows))
    return len(rows)


if __name__ == "__main__":
    run()

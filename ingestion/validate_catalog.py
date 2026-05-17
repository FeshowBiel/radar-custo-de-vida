"""Valida os códigos do catálogo BCB consultando o último valor de cada série."""
import sys

import httpx

from ingestion.logging_config import setup_logging
from ingestion.series_catalog import CATALOGO_BCB

BASE_URL = "https://api.bcb.gov.br/dados/serie"


def validar_codigo(codigo: int) -> tuple[bool, str]:
    url = f"{BASE_URL}/bcdata.sgs.{codigo}/dados/ultimos/1"
    try:
        resp = httpx.get(url, params={"formato": "json"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            ultimo = data[0]
            return True, f"data={ultimo.get('data', '?')} valor={ultimo.get('valor', '?')}"
        return False, "resposta vazia"
    except httpx.HTTPStatusError as e:
        return False, f"HTTP {e.response.status_code}"
    except Exception as e:
        return False, str(e)


def run() -> None:
    setup_logging()
    print(f"\n{'Código':>7}  {'Status':<8}  {'Nome':<40}  {'Detalhe'}")
    print("-" * 90)
    falhas = 0
    for serie in CATALOGO_BCB:
        ok, detalhe = validar_codigo(serie.codigo)
        status = "OK" if ok else "FALHOU"
        marker = "" if ok else " <--"
        print(f"{serie.codigo:>7}  {status:<8}  {serie.nome:<40}  {detalhe}{marker}")
        if not ok:
            falhas += 1
    print(f"\nTotal: {len(CATALOGO_BCB)} séries, {falhas} com falha.\n")
    if falhas:
        sys.exit(1)


if __name__ == "__main__":
    run()

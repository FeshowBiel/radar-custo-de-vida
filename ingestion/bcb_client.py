"""Cliente da API SGS do Banco Central.

A API limita consultas por período a 10 anos. Este cliente pagina
automaticamente em blocos de até 9 anos.
"""
import logging
from datetime import date, datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

BASE_URL = "https://api.bcb.gov.br/dados/serie"
MAX_ANOS_POR_BLOCO = 9


class BCBSeriesError(Exception):
    """Erro irrecuperável ao coletar uma série."""


class BCBClient:
    def __init__(self, timeout: float = 60.0):
        self.client = httpx.Client(timeout=timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True,
    )
    def _fetch_bloco(self, codigo: int, di: str, df: str) -> list[dict]:
        url = f"{BASE_URL}/bcdata.sgs.{codigo}/dados"
        params = {"formato": "json", "dataInicial": di, "dataFinal": df}
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise BCBSeriesError(f"Resposta inesperada para série {codigo}: {data!r}")
        return data

    def get_serie(self, codigo: int, inicio: str = "2006-01-01") -> list[dict]:
        """Coleta a série inteira paginando em blocos de <=9 anos.

        Retorna lista de {'data': 'dd/MM/aaaa', 'valor': 'x.xx'}.
        Levanta BCBSeriesError se nenhum bloco retornar dados.
        """
        dt_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
        dt_fim = date.today()
        resultados: list[dict] = []
        cursor = dt_inicio

        while cursor < dt_fim:
            try:
                bloco_fim = cursor.replace(year=cursor.year + MAX_ANOS_POR_BLOCO)
            except ValueError:  # 29/02 em ano não-bissexto
                bloco_fim = cursor.replace(year=cursor.year + MAX_ANOS_POR_BLOCO, day=28)
            bloco_fim = min(bloco_fim, dt_fim)

            di = cursor.strftime("%d/%m/%Y")
            df = bloco_fim.strftime("%d/%m/%Y")
            logger.debug("Série %d: bloco %s a %s", codigo, di, df)

            try:
                resultados.extend(self._fetch_bloco(codigo, di, df))
            except httpx.HTTPStatusError as e:
                logger.warning("Bloco %s-%s da série %d falhou: %s", di, df, codigo, e)

            cursor = bloco_fim

        if not resultados:
            raise BCBSeriesError(f"Série {codigo} não retornou nenhum dado")
        return resultados

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

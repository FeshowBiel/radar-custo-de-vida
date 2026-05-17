"""Cliente para a API Agregados v3 do IBGE."""
import logging
from datetime import date

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"


class IBGEClient:
    def __init__(self, timeout: float = 60.0):
        self.client = httpx.Client(timeout=timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True,
    )
    def _fetch(self, url: str, params: dict | None = None) -> list:
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_ipca_regional(
        self,
        agregado: int = 7060,
        variavel: int = 63,
        nivel: str = "N1",
        periodos: str = "all",
    ) -> list[dict]:
        """Coleta IPCA por localidade e achata num list de dicts.

        Cada dict contém: codigo_localidade, nome_localidade,
        data_referencia (date), variavel (str), valor (float|None),
        raw_payload (dict da série bruta).
        """
        url = (
            f"{BASE_URL}/{agregado}/periodos/{periodos}/variaveis/{variavel}"
            f"?localidades={nivel}[all]"
        )
        try:
            payload = self._fetch(url)
        except Exception as e:
            logger.warning("IBGE: falha ao buscar dados (%s). Retornando vazio.", e)
            return []

        if not isinstance(payload, list):
            logger.warning("IBGE: resposta inesperada (não é lista). Retornando vazio.")
            return []

        rows: list[dict] = []
        for variavel_obj in payload:
            try:
                nome_variavel = variavel_obj.get("variavel", str(variavel))
                for resultado in variavel_obj.get("resultados", []):
                    for serie_obj in resultado.get("series", []):
                        localidade = serie_obj.get("localidade", {})
                        cod_loc = str(localidade.get("id", ""))
                        nome_loc = str(localidade.get("nome", ""))
                        for periodo, valor_str in serie_obj.get("serie", {}).items():
                            data_ref = _periodo_para_data(periodo)
                            if data_ref is None:
                                continue
                            valor = _parse_valor(valor_str)
                            rows.append(
                                {
                                    "codigo_localidade": cod_loc,
                                    "nome_localidade": nome_loc,
                                    "data_referencia": data_ref,
                                    "variavel": nome_variavel,
                                    "valor": valor,
                                    "raw_payload": serie_obj,
                                }
                            )
            except Exception as e:
                logger.warning("IBGE: erro ao processar item da resposta: %s", e)
                continue

        return rows

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _periodo_para_data(periodo: str) -> date | None:
    """Converte 'aaaamm' para o primeiro dia do mês."""
    try:
        if len(periodo) == 6:
            return date(int(periodo[:4]), int(periodo[4:6]), 1)
    except (ValueError, IndexError):
        pass
    return None


def _parse_valor(s) -> float | None:
    try:
        return float(s)
    except (ValueError, TypeError):
        return None

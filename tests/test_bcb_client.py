"""Testes para BCBClient — paginação, erros e parsing."""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from ingestion.bcb_client import BCBClient, BCBSeriesError


def _mock_response(payload, status_code=200):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    return resp


class TestBCBClientPaginacao:
    def test_serie_curta_um_bloco(self, bcb_payload_valido):
        """Série dentro de 9 anos deve fazer exatamente 1 requisição."""
        with patch("httpx.Client.get", return_value=_mock_response(bcb_payload_valido)):
            with BCBClient() as client:
                result = client.get_serie(433, inicio="2020-01-01")
        assert len(result) == len(bcb_payload_valido)

    def test_serie_longa_dois_blocos(self, bcb_payload_valido):
        """Série de ~15 anos deve paginar em 2 blocos (>=9a)."""
        with patch("httpx.Client.get", return_value=_mock_response(bcb_payload_valido)) as mock_get:
            with BCBClient() as client:
                result = client.get_serie(433, inicio="2006-01-01")
        assert mock_get.call_count >= 2
        assert len(result) > 0

    def test_retorna_vazio_levanta_erro(self, bcb_payload_vazio):
        """Todos blocos retornando vazio deve levantar BCBSeriesError."""
        with patch("httpx.Client.get", return_value=_mock_response(bcb_payload_vazio)):
            with pytest.raises(BCBSeriesError):
                with BCBClient() as client:
                    client.get_serie(99999, inicio="2024-01-01")

    def test_resposta_nao_lista_levanta_erro(self):
        """Resposta que não é lista deve levantar BCBSeriesError."""
        with patch("httpx.Client.get", return_value=_mock_response({"erro": "not a list"})):
            with pytest.raises(BCBSeriesError):
                with BCBClient() as client:
                    client.get_serie(433, inicio="2024-01-01")

    def test_http_error_em_bloco_nao_aborta_serie(self, bcb_payload_valido):
        """Erro HTTP em um bloco deve ser logado, série com outros blocos retorna dados."""
        # Patching _fetch_bloco directly to avoid tenacity retry consuming extra mock responses.
        # First block succeeds, second raises HTTPStatusError, remaining return empty.
        call_count = 0

        def _side_effect(codigo, di, df):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return bcb_payload_valido
            raise httpx.HTTPStatusError(
                "500", request=MagicMock(), response=MagicMock(status_code=500)
            )

        with BCBClient() as client:
            with patch.object(client, "_fetch_bloco", side_effect=_side_effect):
                result = client.get_serie(433, inicio="2006-01-01")
        assert len(result) > 0

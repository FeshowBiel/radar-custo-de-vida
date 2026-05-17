"""Fixtures compartilhadas entre os testes."""
import pytest


@pytest.fixture
def bcb_payload_valido():
    """Payload de exemplo retornado pela API BCB (lista de dicts data/valor)."""
    return [
        {"data": "01/01/2024", "valor": "0.42"},
        {"data": "01/02/2024", "valor": "0.83"},
        {"data": "01/03/2024", "valor": "0.16"},
        {"data": "01/04/2024", "valor": "0.38"},
        {"data": "01/05/2024", "valor": "0.46"},
        {"data": "01/06/2024", "valor": "0.20"},
    ]


@pytest.fixture
def bcb_payload_vazio():
    return []

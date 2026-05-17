"""Testes para o catálogo de séries."""
from ingestion.series_catalog import CATALOGO_BCB

CATEGORIAS_VALIDAS = {"indice_geral", "grupo_ipca", "macro"}
UNIDADES_VALIDAS = {"var_pct_mensal", "pct", "reais"}


def test_catalogo_nao_esta_vazio():
    assert len(CATALOGO_BCB) > 0


def test_todos_codigos_sao_inteiros_positivos():
    for serie in CATALOGO_BCB:
        assert isinstance(serie.codigo, int), f"Código não int: {serie}"
        assert serie.codigo > 0, f"Código não positivo: {serie}"


def test_codigos_sao_unicos():
    codigos = [s.codigo for s in CATALOGO_BCB]
    assert len(codigos) == len(set(codigos)), "Há códigos duplicados no catálogo"


def test_todas_categorias_validas():
    for serie in CATALOGO_BCB:
        assert serie.categoria in CATEGORIAS_VALIDAS, (
            f"Categoria inválida em {serie.nome}: {serie.categoria!r}"
        )


def test_todas_unidades_validas():
    for serie in CATALOGO_BCB:
        assert serie.unidade in UNIDADES_VALIDAS, (
            f"Unidade inválida em {serie.nome}: {serie.unidade!r}"
        )


def test_series_consagradas_presentes():
    """Códigos fundamentais (IPCA, INPC, salário mínimo, Selic) devem existir."""
    codigos = {s.codigo for s in CATALOGO_BCB}
    assert 433 in codigos, "IPCA (433) ausente"
    assert 188 in codigos, "INPC (188) ausente"
    assert 1619 in codigos, "Salário mínimo (1619) ausente"
    assert 432 in codigos, "Selic (432) ausente"

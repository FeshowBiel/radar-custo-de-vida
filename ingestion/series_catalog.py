"""Catálogo de séries econômicas a coletar.

Para adicionar uma série: acrescente uma linha em CATALOGO_BCB.
Para remover: comente ou apague a linha.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SerieBCB:
    codigo: int
    nome: str
    categoria: str  # 'indice_geral' | 'grupo_ipca' | 'macro'
    unidade: str  # 'var_pct_mensal' | 'reais' | 'pct'


# Códigos consagrados: 433, 188, 13522, 1619, 432.
# VALIDATE: 1635-1643 e 24369 podem estar incorretos — o job loga e pula
# códigos que retornarem erro/vazio.
CATALOGO_BCB: list[SerieBCB] = [
    SerieBCB(433, "IPCA", "indice_geral", "var_pct_mensal"),
    SerieBCB(188, "INPC", "indice_geral", "var_pct_mensal"),
    SerieBCB(13522, "IPCA acumulado 12 meses", "indice_geral", "pct"),
    SerieBCB(1635, "IPCA - Alimentacao e bebidas", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1636, "IPCA - Habitacao", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1637, "IPCA - Artigos de residencia", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1638, "IPCA - Vestuario", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1639, "IPCA - Transportes", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1640, "IPCA - Comunicacao", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1641, "IPCA - Saude e cuidados pessoais", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1642, "IPCA - Despesas pessoais", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1643, "IPCA - Educacao", "grupo_ipca", "var_pct_mensal"),
    SerieBCB(1619, "Salario minimo", "macro", "reais"),
    SerieBCB(432, "Selic meta", "macro", "pct"),
    SerieBCB(24369, "Taxa de desocupacao", "macro", "pct"),
]

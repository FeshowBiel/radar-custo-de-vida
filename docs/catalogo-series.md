# Catálogo de Séries Econômicas

Séries coletadas da API SGS do Banco Central do Brasil.
Execute `make validate` para atualizar a coluna **Status**.

| Código | Nome | Categoria | Unidade | Status |
|--------|------|-----------|---------|--------|
| 433 | IPCA | indice_geral | var_pct_mensal | ✅ Validado (2026-05-17) |
| 188 | INPC | indice_geral | var_pct_mensal | ✅ Validado (2026-05-17) |
| 13522 | IPCA acumulado 12 meses | indice_geral | pct | ✅ Validado (2026-05-17) |
| 1635 | IPCA - Alimentação e bebidas | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1636 | IPCA - Habitação | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1637 | IPCA - Artigos de residência | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1638 | IPCA - Vestuário | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1639 | IPCA - Transportes | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1640 | IPCA - Comunicação | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1641 | IPCA - Saúde e cuidados pessoais | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1642 | IPCA - Despesas pessoais | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1643 | IPCA - Educação | grupo_ipca | var_pct_mensal | ✅ Validado (2026-05-17) |
| 1619 | Salário mínimo | macro | reais | ✅ Validado (2026-05-17) |
| 432 | Selic meta | macro | pct | ✅ Validado (2026-05-17) |
| 24369 | Taxa de desocupação (PNAD) | macro | pct | ✅ Validado (2026-05-17) |

> **Resultado da validação (2026-05-17):** todos os 15 códigos retornaram dados —
> inclusive os grupos do IPCA (1635–1643) e a taxa de desocupação (24369),
> que estavam marcados como "verificar" na especificação. 0 falhas.

## Como validar

```bash
make validate
```

O script consulta `/dados/ultimos/1` para cada código e imprime o status atual.
Séries marcadas como ⚠️ serão confirmadas ou corrigidas após a primeira execução.

## Notas

- A API SGS não requer autenticação.
- Paginação máxima: blocos de ≤ 9 anos por requisição (limitação da API desde 03/2025).
- Séries com código inválido são ignoradas silenciosamente no pipeline — apenas logadas como WARNING.

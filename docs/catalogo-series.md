# Catálogo de Séries Econômicas

Séries coletadas da API SGS do Banco Central do Brasil.
Execute `make validate` para atualizar a coluna **Status**.

| Código | Nome | Categoria | Unidade | Status |
|--------|------|-----------|---------|--------|
| 433 | IPCA | indice_geral | var_pct_mensal | ✅ Validado |
| 188 | INPC | indice_geral | var_pct_mensal | ✅ Validado |
| 13522 | IPCA acumulado 12 meses | indice_geral | pct | ✅ Validado |
| 1635 | IPCA - Alimentação e bebidas | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1636 | IPCA - Habitação | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1637 | IPCA - Artigos de residência | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1638 | IPCA - Vestuário | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1639 | IPCA - Transportes | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1640 | IPCA - Comunicação | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1641 | IPCA - Saúde e cuidados pessoais | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1642 | IPCA - Despesas pessoais | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1643 | IPCA - Educação | grupo_ipca | var_pct_mensal | ⚠️ Verificar |
| 1619 | Salário mínimo | macro | reais | ✅ Validado |
| 432 | Selic meta | macro | pct | ✅ Validado |
| 24369 | Taxa de desocupação (PNAD) | macro | pct | ⚠️ Verificar |

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

# Arquitetura — Radar do Custo de Vida

## Fluxo de dados

```
APIs Públicas
    │
    ├── Banco Central (SGS)          ──► ingestion/bcb_client.py
    │   https://api.bcb.gov.br              │
    │   15 séries econômicas                │
    │                                       ▼
    └── IBGE (Agregados v3)         ──► ingestion/ibge_client.py
        IPCA regional                       │
                                            ▼
                               ┌─────────────────────┐
                               │   raw.bcb_series     │  PostgreSQL
                               │   raw.ibge_ipca_     │
                               │   regional           │
                               └─────────┬───────────┘
                                         │
                                    dbt run
                                         │
                         ┌───────────────┼───────────────┐
                         ▼               ▼               ▼
                    staging.*       staging.*        (pass-through)
                    stg_bcb__    stg_ibge__ipca_
                    series       regional
                         │               │
                         └───────┬───────┘
                                 │
                            intermediate.*
                     ┌───────────┴──────────┐
                     ▼                      ▼
              int_ipca_              int_poder_
              acumulado_12m          compra
                     │                      │
                     └───────┬──────────────┘
                             │
                         marts.*
            ┌────────────────┼────────────────────┐
            ▼                ▼                    ▼
     dim_tempo    mart_inflacao_por_    mart_poder_compra_
                  categoria             salario
                             │
                  mart_inflacao_
                  regional
                                             │
                                        ml/save_forecast.py
                                             │
                                    marts.previsao_ipca_raw
                                    marts.previsao_metadata
                                             │
                                      fct_previsao_ipca
                                        (dbt view)
                                             │
                                    ┌────────────────┐
                                    │ Streamlit App  │
                                    │ 5 páginas      │
                                    └────────────────┘
```

## Camadas

| Camada | Schema | Responsabilidade |
|--------|--------|-----------------|
| Ingestão | `raw` | Dados brutos das APIs, sem transformação |
| Staging | `staging` | Limpeza e tipagem; views sobre `raw` |
| Intermediate | `staging` | Lógica de negócio reutilizável (janelas, deflators) |
| Marts | `marts` | Tabelas analíticas otimizadas para o dashboard |
| ML | `marts` | Previsão e metadados, populados por script Python |

## Componentes principais

- **`ingestion/`** — clientes HTTP com retry, catálogo de séries, jobs de upsert
- **`dbt_project/`** — transformações declarativas, testes de dados integrados
- **`ml/`** — SARIMA (padrão) ou Prophet (opcional), backtest walk-forward
- **`dashboard/`** — app Streamlit multipágina, cache de 1h, leitura direto dos marts
- **`.github/workflows/`** — ingestão mensal (dia 12) + transformação + previsão

## Decisões de design

Ver [decisoes-tecnicas.md](decisoes-tecnicas.md).

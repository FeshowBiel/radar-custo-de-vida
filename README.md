# Radar do Custo de Vida no Brasil

Pipeline ELT de dados econômicos oficiais com análise de séries temporais, projeção de
inflação e dashboard interativo.

## O problema

Entender a evolução do custo de vida no Brasil exige cruzar múltiplas fontes de dados
(IPCA por categoria, salário mínimo, Selic, desemprego) que estão dispersas em APIs
governamentais sem interface analítica. Este projeto coleta, transforma e visualiza
essas séries numa stack de dados moderna e reproduzível.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Ingestão | Python · httpx · tenacity |
| Banco | PostgreSQL 16 (Docker local / Neon em prod) |
| Transformação | dbt-core 1.8 + dbt_utils |
| Previsão | SARIMA (statsmodels) · backtest walk-forward |
| Dashboard | Streamlit · Plotly |
| CI/CD | GitHub Actions (cron mensal) |

## Fontes de dados

- **Banco Central — API SGS**: 15 séries econômicas (IPCA, INPC, Selic, salário mínimo, desemprego, grupos do IPCA). Sem autenticação.
- **IBGE — API Agregados v3**: IPCA regional por localidade. Sem autenticação.

## Pré-requisitos

- Python 3.11+
- Docker Desktop
- git

## Como rodar localmente

### 1. Instalar dependências

```bash
cd radar-custo-de-vida
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements-dev.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# .env já vem preenchido para o Docker local — não precisa editar
```

### 3. Subir o banco e criar tabelas

```bash
make db-up      # inicia o container Postgres
make db-init    # cria schemas e tabelas
```

### 4. Executar o pipeline completo (ordem obrigatória)

```bash
make validate   # opcional: verifica quais séries estão acessíveis
make ingest     # coleta dados das APIs → raw.*
make forecast   # treina SARIMA e persiste previsão → marts.*
make dbt-deps   # instala pacotes dbt (primeira vez)
make dbt-run    # materializa staging / intermediate / marts
make dbt-test   # roda testes de qualidade de dados
```

> **Ordem importante:** `forecast` deve rodar **antes** de `dbt-run` porque
> o model `fct_previsao_ipca` lê a tabela `marts.previsao_ipca_raw` criada pelo ML.

### 5. Abrir o dashboard

```bash
make dashboard
# Acesse http://localhost:8501
```

### 6. Testes e lint

```bash
make test   # pytest -q
make lint   # ruff check .
```

### Atalho (pipeline completo de uma vez)

```bash
make all
```

## Modelo de previsão

O módulo `ml/` usa **SARIMA(1,0,1)(1,0,1)[12]** implementado em `statsmodels`.
Se `prophet` estiver instalado (`pip install -r requirements-extra.txt`), ele é
usado automaticamente.

O backtest walk-forward treina o modelo sem os últimos 12 meses e mede o erro
contra o real. As métricas (MAE, RMSE, MAPE) são persistidas em
`marts.previsao_metadata` e exibidas na página de projeção.

> As projeções são estimativas estatísticas com intervalo de confiança de 80%.
> Choques externos (câmbio, commodities, política fiscal) não são capturados pelo modelo.

## Estrutura do projeto

```
radar-custo-de-vida/
├── ingestion/          # clientes HTTP, catálogo de séries, jobs de upsert
├── dbt_project/        # modelos dbt (staging → intermediate → marts)
├── ml/                 # previsão SARIMA, backtest, persistência
├── dashboard/          # app Streamlit (5 páginas)
├── tests/              # testes unitários (pytest)
├── docs/               # arquitetura, catálogo de séries, ADRs, deploy
└── .github/workflows/  # CI/CD mensal
```

## Dependências

| Arquivo | Uso |
|---------|-----|
| `requirements.txt` | Runtime do dashboard (enxuto). Streamlit Cloud instala este. |
| `requirements-pipeline.txt` | Pipeline completo (ingestão + dbt + ML). GitHub Actions usa este. |
| `requirements-dev.txt` | Pipeline + testes/lint. Use localmente. |
| `requirements-extra.txt` | Prophet (opcional). |

## Deploy em produção

Veja [docs/deploy.md](docs/deploy.md) para o checklist completo (Neon + Streamlit Cloud + GitHub Secrets).

## Arquitetura

Veja [docs/arquitetura.md](docs/arquitetura.md) para o diagrama de fluxo de dados.

## Decisões técnicas

Veja [docs/decisoes-tecnicas.md](docs/decisoes-tecnicas.md) para os ADRs do projeto.

## Licença

MIT — veja [LICENSE](LICENSE).

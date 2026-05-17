# Checklist de Deploy — Radar do Custo de Vida

## 1. Criar banco no Neon (https://neon.tech)

1. Crie uma conta gratuita em https://neon.tech
2. Crie um projeto (ex: `radar-custo-de-vida`)
3. Copie a **connection string** no formato:
   ```
   postgresql://user:password@host/dbname?sslmode=require
   ```
4. Salve as partes individualmente (para os GitHub Secrets):
   - `POSTGRES_HOST` — ex: `ep-xxx.us-east-2.aws.neon.tech`
   - `POSTGRES_PORT` — `5432`
   - `POSTGRES_USER` — ex: `radar_owner`
   - `POSTGRES_PASSWORD` — sua senha gerada
   - `POSTGRES_DB` — ex: `radar`
   - `DATABASE_URL` — a connection string completa

## 2. Popular o banco Neon (primeira carga)

No seu terminal local, com o `.env` apontando para o Neon:

```bash
# Edite .env substituindo os valores locais pelos do Neon:
# DATABASE_URL=postgresql://user:password@neon-host/dbname?sslmode=require
# POSTGRES_HOST=...  POSTGRES_USER=...  etc.

# Então rode:
make db-init
make ingest
make forecast
make dbt-run
```

> `make db-init` usa `docker exec` para conectar ao container local.
> Para Neon, use o cliente psql ou qualquer ferramenta SQL:
> `psql "$DATABASE_URL" -f ingestion/sql/001_create_schemas.sql`
> `psql "$DATABASE_URL" -f ingestion/sql/002_create_raw_tables.sql`

## 3. Configurar GitHub Secrets

No repositório GitHub → Settings → Secrets and variables → Actions → New repository secret:

| Secret | Valor |
|--------|-------|
| `DATABASE_URL` | Connection string completa do Neon |
| `POSTGRES_HOST` | Host do Neon |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_USER` | Usuário do Neon |
| `POSTGRES_PASSWORD` | Senha do Neon |
| `POSTGRES_DB` | Nome do banco |

## 4. Deploy no Streamlit Cloud

1. Acesse https://share.streamlit.io e conecte ao GitHub
2. Novo app → selecione o repositório
3. Main file path: `dashboard/app.py`
4. Em **Advanced settings → Secrets**, adicione:
   ```toml
   DATABASE_URL = "postgresql://user:password@neon-host/dbname?sslmode=require"
   ```
5. Clique em **Deploy**

## 5. Verificar

- [ ] Os workflows GitHub Actions rodam sem erro (aba Actions)
- [ ] O dashboard Streamlit Cloud carrega as 5 páginas com dados reais
- [ ] O agendamento mensal (dia 12) dispara automaticamente

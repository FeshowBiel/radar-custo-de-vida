# Windows note: install make via 'choco install make' or 'scoop install make'
# All Python commands use 'python' (Windows). On Linux/macOS change to 'python3'.
# db-init uses docker exec instead of bare psql (psql not required on the host).

.PHONY: setup db-up db-down db-init ingest dbt-deps dbt-run dbt-test forecast dashboard test lint validate all clean

PYTHON  := python
DBT_DIR := dbt_project
export DBT_PROFILES_DIR := $(DBT_DIR)

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

db-up:
	docker compose up -d
	@echo "Aguardando Postgres ficar pronto..."
	@sleep 5

db-down:
	docker compose down

db-init:
	docker exec -i radar-postgres psql -U radar -d radar < ingestion/sql/001_create_schemas.sql
	docker exec -i radar-postgres psql -U radar -d radar < ingestion/sql/002_create_raw_tables.sql

validate:
	$(PYTHON) -m ingestion.validate_catalog

ingest:
	$(PYTHON) -m ingestion.jobs.ingest_bcb_series
	$(PYTHON) -m ingestion.jobs.ingest_ibge_regional

dbt-deps:
	cd $(DBT_DIR) && dbt deps

dbt-run:
	cd $(DBT_DIR) && dbt run

dbt-test:
	cd $(DBT_DIR) && dbt test

forecast:
	$(PYTHON) -m ml.save_forecast

dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q

lint:
	ruff check .

all: db-up db-init ingest dbt-deps dbt-run dbt-test forecast
	@echo "Pipeline completo. Rode 'make dashboard' para visualizar."

clean:
	docker compose down -v

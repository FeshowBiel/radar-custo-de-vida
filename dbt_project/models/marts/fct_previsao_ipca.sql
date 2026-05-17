{{ config(materialized='view') }}

-- Tabela física marts.previsao_ipca_raw é populada por ml/save_forecast.py
select
    data_referencia,
    tipo,            -- 'historico' | 'previsto'
    valor,
    limite_inferior,
    limite_superior
from {{ source('marts_ml', 'previsao_ipca_raw') }}

{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'bcb_series') }}
)

select
    codigo_serie,
    nome_serie,
    categoria,
    unidade,
    data_referencia,
    valor
from source
where valor is not null

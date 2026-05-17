{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'ibge_ipca_regional') }}
)

select
    codigo_localidade,
    nome_localidade,
    data_referencia,
    variavel,
    valor
from source
where valor is not null

{{ config(materialized='table') }}

-- Inflação acumulada por grupo do IPCA, agregada por ano.
with grupos as (
    select
        nome_serie as categoria,
        extract(year from data_referencia)::int as ano,
        valor as var_mensal
    from {{ ref('stg_bcb__series') }}
    where categoria = 'grupo_ipca'
)

select
    categoria,
    ano,
    (exp(sum(ln(1 + var_mensal / 100.0))) - 1) * 100 as inflacao_acumulada_ano,
    count(*) as meses_no_ano
from grupos
group by categoria, ano
order by ano, categoria

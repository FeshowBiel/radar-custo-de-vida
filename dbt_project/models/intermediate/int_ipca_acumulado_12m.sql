{{ config(materialized='view') }}

-- IPCA acumulado em 12 meses, calculado por janela móvel sobre a
-- variação mensal (série 433).
with ipca_mensal as (
    select data_referencia, valor as var_mensal
    from {{ ref('stg_bcb__series') }}
    where codigo_serie = 433
),

acumulado as (
    select
        data_referencia,
        var_mensal,
        exp(sum(ln(1 + var_mensal / 100.0))
            over (order by data_referencia
                  rows between 11 preceding and current row)) - 1
            as fator_12m,
        count(*) over (order by data_referencia
                       rows between 11 preceding and current row) as n_meses
    from ipca_mensal
)

select
    data_referencia,
    var_mensal,
    case when n_meses = 12 then fator_12m * 100 end as ipca_acumulado_12m
from acumulado

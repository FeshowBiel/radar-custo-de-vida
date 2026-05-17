{{ config(materialized='view') }}

-- Deflaciona o salário mínimo nominal pelo IPCA acumulado, produzindo
-- a série de poder de compra real (índice base 100 no primeiro mês).
with salario as (
    select data_referencia, valor as salario_nominal
    from {{ ref('stg_bcb__series') }}
    where codigo_serie = 1619
),

ipca as (
    select data_referencia, valor as ipca_mensal
    from {{ ref('stg_bcb__series') }}
    where codigo_serie = 433
),

base as (
    select s.data_referencia, s.salario_nominal, i.ipca_mensal
    from salario s
    join ipca i using (data_referencia)
),

com_deflator as (
    select
        *,
        exp(sum(ln(1 + ipca_mensal / 100.0))
            over (order by data_referencia)) as deflator_acumulado
    from base
)

select
    data_referencia,
    salario_nominal,
    salario_nominal / deflator_acumulado as salario_real_bruto,
    100.0
        * (salario_nominal / deflator_acumulado)
        / first_value(salario_nominal / deflator_acumulado)
          over (order by data_referencia)
        as indice_poder_compra
from com_deflator

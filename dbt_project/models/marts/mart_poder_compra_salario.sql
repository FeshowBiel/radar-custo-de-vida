{{ config(materialized='table') }}

select
    data_referencia,
    salario_nominal,
    salario_real_bruto,
    indice_poder_compra
from {{ ref('int_poder_compra') }}
order by data_referencia

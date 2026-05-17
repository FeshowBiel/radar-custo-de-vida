{{ config(materialized='table') }}

with meses as (
    select generate_series(
        '2006-01-01'::date,
        date_trunc('month', current_date)::date,
        '1 month'::interval
    )::date as data_referencia
)

select
    data_referencia,
    extract(year  from data_referencia)::int as ano,
    extract(month from data_referencia)::int as mes,
    extract(quarter from data_referencia)::int as trimestre,
    to_char(data_referencia, 'YYYY-MM') as ano_mes
from meses

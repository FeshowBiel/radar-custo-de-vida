{{ config(materialized='table') }}

-- Inflação por localidade. Se a ingestão IBGE estiver vazia,
-- este model resulta em tabela vazia (não quebra o build).
select
    codigo_localidade,
    nome_localidade,
    extract(year from data_referencia)::int as ano,
    variavel,
    avg(valor) as valor_medio
from {{ ref('stg_ibge__ipca_regional') }}
group by codigo_localidade, nome_localidade, ano, variavel
order by ano, nome_localidade

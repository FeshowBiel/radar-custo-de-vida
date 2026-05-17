{#
  Usa o schema customizado (+schema em dbt_project.yml) diretamente,
  sem o prefixo do schema do profile. Assim os models de staging caem
  em `staging` e os de marts em `marts` — alinhado com o que o módulo
  ML e o dashboard esperam.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}

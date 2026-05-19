# Decisões Técnicas — ADRs

## ADR-1: Validar APIs antes de iniciar o build

**Decisão:** Incluir `make validate` que testa cada código de série antes da ingestão.

**Por que:** Os códigos dos grupos do IPCA (1635–1643) e de desocupação (24369) não são
documentados oficialmente com a mesma garantia que 433, 188, 1619 e 432.
Falhar silenciosamente é preferível a abortar o pipeline inteiro — o job loga WARNING
e pula, mantendo todas as outras séries íntegras.

---

## ADR-2: SARIMA como padrão, Prophet opcional

**Decisão:** `ml/forecast.py` usa SARIMA (statsmodels) por padrão. Prophet é detectado
automaticamente se instalado.

**Por que:** `statsmodels` não tem dependências de compilação e instala em segundos em
qualquer plataforma. `prophet` exige compiladores C++ e pode falhar em ambientes restritos
(ex: servidores CI sem build tools). Para a maioria dos cenários de uso, SARIMA(1,0,1)(1,0,1)[12]
é suficientemente preciso para o IPCA mensal.

---

## ADR-3: Exibir intervalo de confiança na projeção

**Decisão:** A página 5 do dashboard exibe a banda IC 80% em vez de apenas o valor pontual.

**Por que:** Apresentar apenas a linha central cria uma falsa sensação de precisão.
O IPCA é influenciado por choques externos (commodities, câmbio, política fiscal) que
um modelo estatístico não captura. Mostrar a incerteza honestamente é responsabilidade
do produto de dados.

---

## ADR-4: Upsert em vez de append na ingestão

**Decisão:** `raw.bcb_series` e `raw.ibge_ipca_regional` usam `ON CONFLICT DO UPDATE`.

**Por que:** As APIs do BCB às vezes retroagem valores de meses recentes (revisões).
Com upsert, rodar `make ingest` duas vezes é idempotente: dados novos entram,
revisões são corrigidas, duplicatas não ocorrem.

---

## ADR-5: Postgres local via Docker para verificação do build

**Decisão:** `docker-compose.yml` sobe Postgres 16 local para desenvolvimento e CI local.
O Neon (Postgres gerenciado) é usado somente para produção.

**Por que:** Isola o ambiente de desenvolvimento, não exige conta em nuvem para rodar
o pipeline completo, e garante reprodutibilidade. A única diferença entre local e
produção é a `DATABASE_URL` e o `sslmode`.

---

## ADR-6: Leitura direta de `raw.bcb_series` no módulo ML

**Decisão:** `ml/data.py` lê `raw.bcb_series` diretamente, sem depender da view dbt
`staging.stg_bcb__series`.

**Por que:** Evita dependência de ordem de execução (dbt precisa ter rodado ao menos
uma vez antes do ML). A view de staging apenas filtra `valor IS NOT NULL` e renomeia
colunas — a mesma lógica cabe em uma linha SQL no módulo Python.

---

## ADR-7: requirements.txt enxuto separado do pipeline

**Decisão:** `requirements.txt` contém só o runtime do dashboard
(streamlit, plotly, pandas, sqlalchemy, psycopg2, dotenv). Pipeline e ML
(httpx, tenacity, dbt-core, statsmodels, scikit-learn) ficam em
`requirements-pipeline.txt`.

**Por que:** O Streamlit Community Cloud instala o `requirements.txt` da raiz.
Incluir dbt-core + statsmodels + scikit-learn (e suas dezenas de deps
transitivas) fazia o build do deploy levar 15+ minutos / travar, sendo que
o dashboard apenas lê tabelas prontas do Postgres — não importa nenhuma
dessas bibliotecas. O CI (`pip install -r requirements-pipeline.txt`) e o
ambiente local (`requirements-dev.txt`) continuam com o conjunto completo.

---

## ADR-8: batch no executemany para Postgres remoto

**Decisão:** O engine SQLAlchemy usa `executemany_mode="values_plus_batch"`.

**Por que:** Contra um Postgres remoto (Neon), o `executemany` linha-a-linha
padrão do psycopg2 fazia a série diária da Selic (~7,4k linhas) levar 20+
minutos — estourando o timeout de 15 min do job de ingestão no GitHub
Actions. Com batching (`execute_batch`), a ingestão completa das 15 séries
caiu para ~44 s.

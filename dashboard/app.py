"""Radar do Custo de Vida no Brasil — página inicial."""
import streamlit as st

from dashboard.lib.queries import inflacao_por_categoria, ipca_acumulado_12m, poder_de_compra

st.set_page_config(
    page_title="Radar do Custo de Vida no Brasil",
    page_icon="R$",
    layout="wide",
)

st.title("Radar do Custo de Vida no Brasil")
st.markdown(
    "Painel analítico de inflação, poder de compra e projeção econômica, "
    "com dados oficiais do **Banco Central** e do **IBGE**.\n\n"
    "> As projeções são estimativas estatísticas com intervalo de confiança, "
    "não previsões garantidas."
)

try:
    ipca12 = ipca_acumulado_12m()
    cat = inflacao_por_categoria()
    pc = poder_de_compra()

    c1, c2, c3 = st.columns(3)
    c1.metric("IPCA acum. 12m", f"{ipca12['ipca_acumulado_12m'].iloc[-1]:.2f}%")

    ultimo_ano = cat["ano"].max()
    top = cat[cat["ano"] == ultimo_ano].nlargest(1, "inflacao_acumulada_ano")
    c2.metric(
        f"Categoria que mais subiu ({ultimo_ano})",
        top["categoria"].iloc[0].replace("IPCA - ", ""),
    )

    c3.metric(
        "Índice de poder de compra do salário",
        f"{pc['indice_poder_compra'].iloc[-1]:.1f}",
        help="Base 100 no início da série",
    )

    st.caption("Use a navegação à esquerda para explorar cada análise.")

except Exception as e:  # noqa: BLE001
    st.error(f"Não foi possível carregar os dados: {e}")
    st.info("Verifique se o pipeline rodou: make ingest → make forecast → make dbt-run")

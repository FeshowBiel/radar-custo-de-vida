"""Inflação regional por localidade (dados IBGE)."""
import plotly.express as px
import streamlit as st

from dashboard.lib.queries import inflacao_regional

st.set_page_config(page_title="Inflação Regional", layout="wide")
st.title("Inflação Regional")

try:
    df = inflacao_regional()

    if df.empty:
        st.info(
            "Dados regionais do IBGE não disponíveis nesta execução. "
            "A tabela `marts.mart_inflacao_regional` está vazia — "
            "verifique os logs do job `ingest_ibge_regional`."
        )
    else:
        anos = sorted(df["ano"].unique(), reverse=True)
        ano_sel = st.selectbox("Ano", anos)
        df_ano = df[df["ano"] == ano_sel].copy()

        fig = px.bar(
            df_ano,
            x="nome_localidade",
            y="valor_medio",
            color="nome_localidade",
            title=f"Inflação média por localidade — {ano_sel}",
            labels={"valor_medio": "Inflação média (%)", "nome_localidade": "Localidade"},
            text_auto=".2f",
        )
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df_ano[["nome_localidade", "variavel", "valor_medio"]]
            .sort_values("valor_medio", ascending=False)
            .reset_index(drop=True)
        )

except Exception as e:  # noqa: BLE001
    st.error(f"Erro ao carregar dados: {e}")

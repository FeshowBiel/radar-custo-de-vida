"""Inflação por categoria — barras horizontais e evolução histórica."""
import plotly.express as px
import streamlit as st
from lib.queries import inflacao_por_categoria

st.set_page_config(page_title="Inflação por Categoria", layout="wide")
st.title("Inflação por Categoria")

try:
    df = inflacao_por_categoria()

    anos = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.selectbox("Ano de referência", anos)

    df_ano = (
        df[df["ano"] == ano_sel]
        .sort_values("inflacao_acumulada_ano", ascending=True)
        .copy()
    )
    df_ano["categoria_curta"] = df_ano["categoria"].str.replace("IPCA - ", "", regex=False)

    fig_bar = px.bar(
        df_ano,
        x="inflacao_acumulada_ano",
        y="categoria_curta",
        orientation="h",
        title=f"Inflação acumulada por categoria — {ano_sel}",
        labels={"inflacao_acumulada_ano": "Inflação acumulada (%)", "categoria_curta": ""},
        color="inflacao_acumulada_ano",
        color_continuous_scale="RdYlGn_r",
        text_auto=".2f",
    )
    fig_bar.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Evolução histórica por categoria")
    categorias = sorted(df["categoria"].str.replace("IPCA - ", "", regex=False).unique())
    selecionadas = st.multiselect(
        "Selecione até 4 categorias",
        categorias,
        default=categorias[:3],
        max_selections=4,
    )

    if selecionadas:
        df_hist = df[
            df["categoria"].str.replace("IPCA - ", "", regex=False).isin(selecionadas)
        ].copy()
        df_hist["categoria_curta"] = df_hist["categoria"].str.replace("IPCA - ", "", regex=False)

        fig_line = px.line(
            df_hist,
            x="ano",
            y="inflacao_acumulada_ano",
            color="categoria_curta",
            title="Inflação anual acumulada por categoria",
            labels={"inflacao_acumulada_ano": "Inflação (%)", "ano": "Ano", "categoria_curta": ""},
            markers=True,
        )
        st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:  # noqa: BLE001
    st.error(f"Erro ao carregar dados: {e}")

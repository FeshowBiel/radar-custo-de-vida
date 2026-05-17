"""Panorama — série histórica do IPCA mensal e acumulado 12m."""
import plotly.graph_objects as go
import streamlit as st

from dashboard.lib.queries import ipca_acumulado_12m, ipca_mensal

st.set_page_config(page_title="Panorama IPCA", layout="wide")
st.title("Panorama da Inflação")

try:
    mensal = ipca_mensal()
    acum12 = ipca_acumulado_12m()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=mensal["data_referencia"],
            y=mensal["valor"],
            name="IPCA mensal (%)",
            line=dict(color="#2E7D32"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=acum12["data_referencia"],
            y=acum12["ipca_acumulado_12m"],
            name="IPCA acum. 12m (%)",
            line=dict(color="#FF6F00", dash="dash"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="IPCA — Variação Mensal e Acumulado 12 Meses",
        xaxis_title="Data",
        yaxis=dict(title="Variação mensal (%)"),
        yaxis2=dict(title="Acumulado 12m (%)", overlaying="y", side="right"),
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15),
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimos 12 meses")
    ultimos = mensal.tail(12).copy()
    ultimos["data_referencia"] = ultimos["data_referencia"].astype(str)
    ultimos.columns = ["Data", "Variação (%)"]
    st.dataframe(ultimos.sort_values("Data", ascending=False).reset_index(drop=True))

except Exception as e:  # noqa: BLE001
    st.error(f"Erro ao carregar dados: {e}")

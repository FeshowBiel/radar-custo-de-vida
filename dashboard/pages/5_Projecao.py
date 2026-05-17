"""Projeção do IPCA — histórico + previsão com banda de incerteza."""
import json

import plotly.graph_objects as go
import streamlit as st

from dashboard.lib.queries import previsao_ipca, previsao_metadata

st.set_page_config(page_title="Projeção IPCA", layout="wide")
st.title("Projeção do IPCA")
st.markdown(
    "O modelo usa **SARIMA** (ou Prophet se instalado) treinado na série histórica do IPCA. "
    "A banda representa o intervalo de confiança de 80% da previsão."
)

try:
    df = previsao_ipca()
    df["data_referencia"] = df["data_referencia"].astype(str)

    hist = df[df["tipo"] == "historico"]
    prev = df[df["tipo"] == "previsto"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hist["data_referencia"],
            y=hist["valor"],
            name="Histórico",
            line=dict(color="#2E7D32"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=prev["data_referencia"],
            y=prev["limite_superior"],
            name="Limite superior (IC 80%)",
            line=dict(width=0),
            showlegend=False,
            mode="lines",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prev["data_referencia"],
            y=prev["limite_inferior"],
            name="Banda de incerteza (IC 80%)",
            fill="tonexty",
            fillcolor="rgba(255,111,0,0.2)",
            line=dict(width=0),
            mode="lines",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prev["data_referencia"],
            y=prev["valor"],
            name="Previsão",
            line=dict(color="#FF6F00", dash="dash", width=2),
        )
    )

    fig.update_layout(
        title="IPCA — Série histórica e previsão para os próximos 12 meses",
        xaxis_title="Data",
        yaxis_title="IPCA variação mensal (%)",
        hovermode="x unified",
        height=460,
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Métricas de qualidade do modelo (backtest)")
    try:
        meta = previsao_metadata()
        if not meta.empty:
            metricas = meta["metricas"].iloc[0]
            if isinstance(metricas, str):
                metricas = json.loads(metricas)
            c1, c2, c3 = st.columns(3)
            c1.metric("MAE", f"{metricas.get('mae', '—'):.4f} p.p.")
            c2.metric("RMSE", f"{metricas.get('rmse', '—'):.4f} p.p.")
            mape = metricas.get("mape")
            c3.metric("MAPE", f"{mape:.2f}%" if mape else "—")
            st.caption(
                f"Backtest com horizonte de {metricas.get('horizonte', 12)} meses. "
                "MAE e RMSE estão em pontos percentuais (p.p.). "
                "Esses valores indicam a margem de erro histórica do modelo — "
                "a previsão futura pode divergir mais em cenários de choque econômico."
            )
    except Exception:  # noqa: BLE001
        st.info("Métricas de backtest não disponíveis.")

except Exception as e:  # noqa: BLE001
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Execute `make forecast` para gerar a previsão.")

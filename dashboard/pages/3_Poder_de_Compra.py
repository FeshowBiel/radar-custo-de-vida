"""Poder de compra do salário mínimo + simulador interativo."""
import plotly.graph_objects as go
import streamlit as st

from dashboard.lib.queries import poder_de_compra

st.set_page_config(page_title="Poder de Compra", layout="wide")
st.title("Poder de Compra do Salário Mínimo")

try:
    df = poder_de_compra()
    df["data_referencia"] = df["data_referencia"].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["data_referencia"],
            y=df["indice_poder_compra"],
            name="Índice poder de compra (base 100)",
            line=dict(color="#2E7D32"),
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.08)",
        )
    )
    fig.update_layout(
        title="Índice de Poder de Compra do Salário Mínimo (Base 100 = primeiro mês da série)",
        xaxis_title="Data",
        yaxis_title="Índice",
        height=420,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Simulador de Poder de Compra")
    anos_disp = sorted(df["data_referencia"].str[:4].unique().astype(int))
    ano_base = st.slider(
        "Ano de referência", int(anos_disp[0]), int(anos_disp[-2]), int(anos_disp[0])
    )

    df_base = df[df["data_referencia"].str.startswith(str(ano_base))]
    df_atual = df.tail(1)

    if not df_base.empty and not df_atual.empty:
        pc_base = float(df_base["indice_poder_compra"].iloc[0])
        pc_atual = float(df_atual["indice_poder_compra"].iloc[0])
        sal_base = float(df_base["salario_nominal"].iloc[0])
        sal_atual = float(df_atual["salario_nominal"].iloc[0])

        fator = pc_atual / pc_base if pc_base else 1.0
        valor_sim = st.number_input(
            f"Valor em {ano_base} (R$)", min_value=1.0, value=float(sal_base), step=50.0
        )
        equivalente = valor_sim * fator

        col1, col2, col3 = st.columns(3)
        col1.metric(f"Valor em {ano_base}", f"R$ {valor_sim:,.2f}")
        col2.metric("Equivalente hoje (poder de compra)", f"R$ {equivalente:,.2f}")
        col3.metric("Variação do índice", f"{(fator - 1) * 100:+.1f}%")

        data_ref = df_atual["data_referencia"].iloc[0]
        st.caption(
            f"Cálculo baseado na variação do índice de poder de compra entre "
            f"jan/{ano_base} e {data_ref}. Salário mínimo nominal: "
            f"R$ {sal_base:,.0f} → R$ {sal_atual:,.0f}."
        )

except Exception as e:  # noqa: BLE001
    st.error(f"Erro ao carregar dados: {e}")

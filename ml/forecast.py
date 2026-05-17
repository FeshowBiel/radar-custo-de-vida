"""Modelo de previsão do IPCA.

Padrão: SARIMA (statsmodels), sem dependência de compilação.
Opcional: Prophet, usado automaticamente se estiver instalado.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _prever_sarima(df: pd.DataFrame, meses: int) -> pd.DataFrame:
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    serie = df.set_index("data_referencia")["valor"].asfreq("MS")
    modelo = SARIMAX(
        serie,
        order=(1, 0, 1),
        seasonal_order=(1, 0, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    ajuste = modelo.fit(disp=False)
    fc = ajuste.get_forecast(steps=meses)
    ic = fc.conf_int(alpha=0.20)  # intervalo de 80%

    return pd.DataFrame(
        {
            "data_referencia": fc.predicted_mean.index,
            "valor": fc.predicted_mean.values,
            "limite_inferior": ic.iloc[:, 0].values,
            "limite_superior": ic.iloc[:, 1].values,
        }
    )


def _prever_prophet(df: pd.DataFrame, meses: int) -> pd.DataFrame:
    from prophet import Prophet

    treino = df.rename(columns={"data_referencia": "ds", "valor": "y"})
    m = Prophet(
        seasonality_mode="additive",
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.80,
    )
    m.fit(treino)
    futuro = m.make_future_dataframe(periods=meses, freq="MS")
    previsao = m.predict(futuro).tail(meses)

    return pd.DataFrame(
        {
            "data_referencia": previsao["ds"].values,
            "valor": previsao["yhat"].values,
            "limite_inferior": previsao["yhat_lower"].values,
            "limite_superior": previsao["yhat_upper"].values,
        }
    )


def _prophet_disponivel() -> bool:
    try:
        import prophet  # noqa: F401

        return True
    except ImportError:
        return False


def prever(df: pd.DataFrame, meses: int = 12) -> pd.DataFrame:
    """Gera previsão do IPCA para os próximos `meses`.

    Retorna DataFrame com colunas:
    data_referencia, valor, limite_inferior, limite_superior.
    """
    if _prophet_disponivel():
        logger.info("Usando Prophet para a previsão")
        return _prever_prophet(df, meses)
    logger.info("Usando SARIMA para a previsão")
    return _prever_sarima(df, meses)

"""Testes para o módulo de backtest."""
import numpy as np
import pandas as pd
import pytest

from ml.backtest import backtest


def _serie_sintetica(n: int = 200) -> pd.DataFrame:
    datas = pd.date_range("2006-01-01", periods=n, freq="MS")
    valores = np.random.default_rng(42).normal(loc=0.5, scale=0.3, size=n)
    return pd.DataFrame({"data_referencia": datas, "valor": valores})


def _previsao_media(df: pd.DataFrame, meses: int) -> pd.DataFrame:
    """Previsor trivial: sempre prevê a média histórica."""
    media = float(df["valor"].mean())
    datas = pd.date_range(df["data_referencia"].iloc[-1], periods=meses + 1, freq="MS")[1:]
    return pd.DataFrame(
        {
            "data_referencia": datas,
            "valor": [media] * meses,
            "limite_inferior": [media - 1] * meses,
            "limite_superior": [media + 1] * meses,
        }
    )


def test_backtest_retorna_chaves_esperadas():
    df = _serie_sintetica()
    resultado = backtest(df, _previsao_media, horizonte=12)
    assert set(resultado.keys()) == {"mae", "rmse", "mape", "horizonte"}


def test_backtest_valores_numericos():
    df = _serie_sintetica()
    resultado = backtest(df, _previsao_media, horizonte=12)
    assert resultado["mae"] >= 0
    assert resultado["rmse"] >= 0
    assert resultado["horizonte"] == 12


def test_backtest_serie_curta_levanta_erro():
    df_curto = _serie_sintetica(n=30)
    with pytest.raises(ValueError, match="curta demais"):
        backtest(df_curto, _previsao_media, horizonte=12)


def test_backtest_mape_none_quando_zeros():
    """MAPE deve ser None quando a série tem zeros (divisão por zero)."""
    n = 60
    datas = pd.date_range("2006-01-01", periods=n, freq="MS")
    # Últimos 12 meses são zero → MAPE indefinido
    valores = [0.5] * (n - 12) + [0.0] * 12
    df = pd.DataFrame({"data_referencia": datas, "valor": valores})
    resultado = backtest(df, _previsao_media, horizonte=12)
    assert resultado["mape"] is None

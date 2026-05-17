"""Backtest do modelo de previsão.

Treina sem os últimos N meses e mede o erro contra o real conhecido.
"""
import numpy as np
import pandas as pd


def backtest(df: pd.DataFrame, funcao_prever, horizonte: int = 12) -> dict:
    """Retorna {'mae', 'rmse', 'mape', 'horizonte'}.

    funcao_prever deve ter assinatura (df, meses) -> DataFrame com coluna 'valor'.
    """
    if len(df) <= horizonte + 24:
        raise ValueError("Série curta demais para backtest confiável")

    treino = df.iloc[:-horizonte].reset_index(drop=True)
    teste = df.iloc[-horizonte:].reset_index(drop=True)

    previsao = funcao_prever(treino, horizonte)

    y_pred = previsao["valor"].to_numpy()[:horizonte]
    y_real = teste["valor"].to_numpy()
    erro = y_real - y_pred

    mae = float(np.mean(np.abs(erro)))
    rmse = float(np.sqrt(np.mean(erro**2)))
    mask = y_real != 0
    mape = float(np.mean(np.abs(erro[mask] / y_real[mask])) * 100) if mask.any() else None

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2) if mape is not None else None,
        "horizonte": horizonte,
    }

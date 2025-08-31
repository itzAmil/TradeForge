# visualization/utils.py

import pandas as pd
import joblib
import streamlit as st
from pathlib import Path

def load_ml_predictions(symbol: str, interval: str, model_path: str = "ml/model_rf.pkl") -> pd.DataFrame | None:
    """
    Loads predictions from CSV and applies ML model.

    Returns:
        pd.DataFrame: Data with 'prediction' column
    """
    csv_path = Path(f"data/{symbol}_{interval}_labeled.csv")
    model_path = Path(model_path)

    if not csv_path.exists():
        st.warning(f"Data file not found: {csv_path}")
        return None
    if not model_path.exists():
        st.warning(f"Model file not found: {model_path}")
        return None

    try:
        df = pd.read_csv(csv_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        model = joblib.load(model_path)
        df["prediction"] = model.predict(df[["sma", "ema", "rsi"]])
        return df
    except Exception as e:
        st.error(f"ML prediction failed: {e}")
        return None

def overlay_ml_predictions(fig, df):
    """
    Adds ML buy/sell markers to chart.
    """
    if "prediction" not in df.columns:
        return fig

    buy_signals = df[df["prediction"] == 1]
    sell_signals = df[df["prediction"] == -1]

    fig.add_scatter(
        x=buy_signals["timestamp"], y=buy_signals["close"],
        mode="markers", name="ML Buy",
        marker=dict(color="green", symbol="triangle-up", size=10)
    )
    fig.add_scatter(
        x=sell_signals["timestamp"], y=sell_signals["close"],
        mode="markers", name="ML Sell",
        marker=dict(color="red", symbol="triangle-down", size=10)
    )
    return fig

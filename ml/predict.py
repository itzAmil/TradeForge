# ml/predict.py

import pandas as pd
import joblib
import os

from ml.feature_engineering import compute_technical_indicators

# === Constants ===
MODEL_PATH = os.path.join("ml", "models", "random_forest.pkl")
FEATURES = [
    "sma_10", "sma_50",
    "ema_10", "ema_50",
    "rsi", "macd", "signal_line",
    "bollinger_upper", "bollinger_lower",
    "returns"
]

# === Load model once ===
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError(f"Model not found at {MODEL_PATH}. Train and save the model before predicting.")

# === Prediction Function ===
def predict_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators and return ML predictions (+1: Buy, -1: Sell, 0: Hold).

    Parameters:
        df (pd.DataFrame): OHLCV DataFrame with at least a 'close' column.

    Returns:
        pd.DataFrame: Copy of input with 'prediction' column added.
    """
    if "close" not in df.columns:
        raise ValueError("Input DataFrame must contain a 'close' column")

    df = df.copy()

    # Compute indicators
    df = compute_technical_indicators(df)

    # Check features
    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    # Drop rows with NaN (from rolling indicators)
    df.dropna(inplace=True)
    if df.empty:
        raise ValueError("No rows left after dropping NaNs. Check input data length.")

    # Predict
    X = df[FEATURES]
    df["prediction"] = model.predict(X)

    return df

# ml/feature_engineering.py

import pandas as pd
import numpy as np

def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute key technical indicators:
    - SMA, EMA
    - RSI
    - MACD
    - Bollinger Bands
    - Returns

    Parameters:
        df (pd.DataFrame): Input OHLCV DataFrame with 'close' column.

    Returns:
        pd.DataFrame: Enhanced DataFrame with indicators.
    """
    df = df.copy()

    # Ensure close column is float
    df['close'] = df['close'].astype(float)

    # === Moving Averages ===
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # === RSI (14) ===
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['rsi'] = 100 - (100 / (1 + rs))

    # === MACD ===
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema_12 - ema_26
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()

    # === Bollinger Bands (20) ===
    sma_20 = df['close'].rolling(window=20).mean()
    std_20 = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = sma_20 + (2 * std_20)
    df['bollinger_lower'] = sma_20 - (2 * std_20)

    # === Returns ===
    df['returns'] = df['close'].pct_change()

    return df.dropna()

#signal_engine/indicators_core.py

import pandas as pd

# -----------------------------------------------
# TradeForge Technical Indicator Calculation Core
# -----------------------------------------------

def calculate_sma(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA) over a specified period.

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'close' column.
        period (int): Lookback window size for SMA.

    Returns:
        pd.Series: SMA values.
    """
    return df["close"].rolling(window=period).mean()


def calculate_ema(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA) over a specified period.

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'close' column.
        period (int): Lookback window size for EMA.

    Returns:
        pd.Series: EMA values.
    """
    return df["close"].ewm(span=period, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI).

    RSI measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions.

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' prices.
        period (int): Number of periods for calculation (default: 14).

    Returns:
        pd.Series: RSI values.
    """
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(window=period).mean()

    rs = gain / (loss + 1e-10)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi.rename(f"RSI_{period}")


def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Moving Average Convergence Divergence (MACD) components.

    MACD Line = EMA(12) - EMA(26)
    Signal Line = EMA(9) of MACD
    Histogram = MACD - Signal

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' prices.

    Returns:
        pd.DataFrame: DataFrame with ['MACD', 'Signal_Line', 'Histogram'] columns.
    """
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    return pd.DataFrame({
        "MACD": macd_line,
        "Signal_Line": signal_line,
        "Histogram": histogram
    })

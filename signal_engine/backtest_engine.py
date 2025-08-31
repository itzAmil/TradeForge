# signal_engine/backtest_engine.py
"""
TradeForge - Backtesting Engine
Generates trading signals and simulates strategy performance.
"""

import pandas as pd
import numpy as np


def generate_signals(
    df: pd.DataFrame,
    rsi_buy: int = 30,
    rsi_sell: int = 70,
    use_rsi: bool = True,
    use_sma: bool = True,
) -> pd.DataFrame:
    """
    Generate trading signals using SMA crossover and/or RSI thresholds.

    Parameters:
        df (pd.DataFrame): Must contain ['close', 'SMA_short', 'SMA_long', 'RSI'].
        rsi_buy (int): RSI threshold to trigger a BUY.
        rsi_sell (int): RSI threshold to trigger a SELL.
        use_rsi (bool): Whether to include RSI in signal logic.
        use_sma (bool): Whether to include SMA crossover in signal logic.

    Returns:
        pd.DataFrame with a 'signal' column:
            1 = buy, -1 = sell, 0 = hold
    """
    df = df.copy()
    df["signal"] = 0

    # --- SMA crossover ---
    if use_sma and "SMA_short" in df.columns and "SMA_long" in df.columns:
        df.loc[df["SMA_short"] > df["SMA_long"], "signal"] = 1
        df.loc[df["SMA_short"] < df["SMA_long"], "signal"] = -1

    # --- RSI override ---
    if use_rsi and "RSI" in df.columns:
        df.loc[df["RSI"] < rsi_buy, "signal"] = 1
        df.loc[df["RSI"] > rsi_sell, "signal"] = -1

    return df


def simulate_backtest(df: pd.DataFrame, initial_balance: float = 10000.0):
    """
    Simulates a backtest for the given trading signals.

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' and 'signal'.
        initial_balance (float): Starting balance.

    Returns:
        (df_with_portfolio, metrics_dict)
    """
    df = df.copy()
    if "signal" not in df.columns:
        raise ValueError("DataFrame must contain 'signal' column.")

    balance = initial_balance
    position = 0
    portfolio_values = []
    trades = []

    for i, row in df.iterrows():
        price = row["close"]
        signal = row["signal"]

        # --- Buy ---
        if signal == 1 and position == 0:
            position = balance / price
            balance = 0
            trades.append({"type": "BUY", "price": price, "time": i})

        # --- Sell ---
        elif signal == -1 and position > 0:
            balance = position * price
            position = 0
            trades.append({"type": "SELL", "price": price, "time": i})

        # --- Track Portfolio ---
        portfolio_value = balance + position * price
        portfolio_values.append(portfolio_value)

    df["portfolio_value"] = portfolio_values

    # ---- Metrics ----
    returns = df["portfolio_value"].pct_change().dropna()
    total_return = (df["portfolio_value"].iloc[-1] / initial_balance) - 1
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

    rolling_max = df["portfolio_value"].cummax()
    drawdown = (df["portfolio_value"] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    wins = [
        1 for j in range(1, len(trades))
        if trades[j]["type"] == "SELL" and trades[j]["price"] > trades[j-1]["price"]
    ]
    win_rate = len(wins) / (len(trades) // 2) if len(trades) >= 2 else 0

    metrics = {
        "Final Portfolio Value": df["portfolio_value"].iloc[-1],
        "Total Return": total_return,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Win Rate": win_rate,
        "Number of Trades": len(trades)
    }

    return df, metrics

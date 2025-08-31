# streamlit_app/pages/14_Chart_Visualizer.py
"""
Chart_Visualizer.py
-------------------
Streamlit page for plotting OHLCV candlestick chart with SMA/EMA/RSI,
buy/sell signals, and equity curve.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def plot_ohlcv_with_signals(
    df: pd.DataFrame,
    show_sma=True,
    show_ema=True,
    show_rsi=True,
    portfolio=None
):
    """
    Plots OHLCV candlestick chart with optional indicators and portfolio equity curve.
    df must contain columns: ['open', 'high', 'low', 'close', 'sma', 'ema', 'rsi', 'signal']
    """
    fig = go.Figure()

    # Ensure timestamps are datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df = df.reset_index()
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )
    )

    # SMA/EMA overlays
    if show_sma and 'sma' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['sma'],
                line=dict(color='blue', width=1.5),
                name='SMA'
            )
        )
    if show_ema and 'ema' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema'],
                line=dict(color='orange', width=1.5),
                name='EMA'
            )
        )

    # RSI as separate y-axis
    if show_rsi and 'rsi' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['rsi'],
                line=dict(color='green', width=1),
                name='RSI',
                yaxis='y2'
            )
        )
        fig.update_layout(
            yaxis2=dict(
                overlaying='y',
                side='right',
                title='RSI',
                showgrid=False
            )
        )

    # Buy/Sell markers
    if 'signal' in df.columns:
        buys = df[df['signal'] == 1]
        sells = df[df['signal'] == -1]

        if not buys.empty:
            fig.add_trace(
                go.Scatter(
                    x=buys['timestamp'],
                    y=buys['close'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', color='green', size=12),
                    name='Buy'
                )
            )
        if not sells.empty:
            fig.add_trace(
                go.Scatter(
                    x=sells['timestamp'],
                    y=sells['close'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', color='red', size=12),
                    name='Sell'
                )
            )

    # Equity curve
    if portfolio is not None and 'total' in portfolio:
        eq = portfolio['total'].copy()
        eq[eq <= 0] = None  # hide zero-value spikes
        fig.add_trace(
            go.Scatter(
                x=eq.index,
                y=eq.values,
                line=dict(color='purple', width=2, dash='dot'),
                name='Equity Curve'
            )
        )

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Price',
        template='plotly_dark',
        legend=dict(orientation='h', y=1.05),
        height=700
    )

    return fig


# === Streamlit Page ===
def main():
    st.title("📊 Chart Visualizer")

    st.write("This page shows candlestick chart with indicators and signals.")

    # For now, create a sample dataset if none is loaded
    # Later, you can replace this with DB fetch or live stream
    dates = pd.date_range("2025-01-01", periods=50, freq="D")
    data = pd.DataFrame({
        "timestamp": dates,
        "open": pd.Series(range(50)) + 100,
        "high": pd.Series(range(50)) + 105,
        "low": pd.Series(range(50)) + 95,
        "close": pd.Series(range(50)) + 100,
        "sma": pd.Series(range(50)) + 98,
        "ema": pd.Series(range(50)) + 99,
        "rsi": pd.Series([50 + (i % 10) for i in range(50)]),
        "signal": [1 if i % 10 == 0 else -1 if i % 15 == 0 else 0 for i in range(50)]
    })

    fig = plot_ohlcv_with_signals(data)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

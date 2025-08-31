# streamlit_app/pages/12_Backtest_Analyzer.py

import os
import sys
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

# --- Add project root to sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# --- Import indicator + backtest functions ---
from signal_engine.indicators_core import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
)
from signal_engine.backtest_engine import generate_signals, simulate_backtest

# --- Page Config ---
st.set_page_config(page_title="Technical Analysis & Backtest", page_icon="📊", layout="wide")
st.title("Backtest Analyzer")
st.write(
    "Upload OHLCV CSV data to compute technical indicators and simulate trading strategies."
)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload CSV (must include 'close' column)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='utf-8').dropna()

    # --- Compute Technical Indicators ---
    st.subheader("Technical Analysis Indicators")
    if "SMA_14" not in df.columns:
        df["SMA_14"] = calculate_sma(df, 14)
    if "EMA_14" not in df.columns:
        df["EMA_14"] = calculate_ema(df, 14)
    if "RSI_14" not in df.columns:
        df["RSI_14"] = calculate_rsi(df, 14)
    if not set(["MACD", "Signal_Line", "Histogram"]).issubset(df.columns):
        macd_df = calculate_macd(df)
        df = pd.concat([df, macd_df], axis=1)

    st.dataframe(
        df[["close", "SMA_14", "EMA_14", "RSI_14", "MACD", "Signal_Line", "Histogram"]].head(20)
    )

    # --- Strategy Backtest ---
    st.subheader("Strategy Backtest")
    initial_balance = st.number_input("Initial Balance ($)", value=10000.0, step=1000.0)

    if st.button("Run Backtest"):
        # --- Column Normalization ---
        column_map = {
            "SMA_short": ["SMA_14", "sma_10"],
            "SMA_long": ["SMA_50", "sma_50"],
            "EMA_short": ["EMA_14", "ema_10"],
            "EMA_long": ["EMA_50", "ema_50"],
            "RSI": ["RSI_14", "rsi"],
            "MACD": ["MACD", "macd"],
            "Signal_Line": ["Signal_Line", "signal_line"],
            "Histogram": ["Histogram", "histogram"]
        }
        for target, options in column_map.items():
            for col in options:
                if col in df.columns:
                    df.rename(columns={col: target}, inplace=True)
                    break

        # --- Generate Signals ---
        df_signals = generate_signals(df)
        st.write("Signals Preview (Last 20 Records)")
        st.dataframe(df_signals[["close", "signal"]].tail(20))

        # --- Run Backtest ---
        df_backtest, metrics = simulate_backtest(df_signals, initial_balance=initial_balance)

        # Display last 10 records
        st.write("Backtest Results (Last 10 Records)")
        st.dataframe(df_backtest.tail(10))

        # --- Price & Signals Plot ---
        st.write("Price with Buy/Sell Signals")
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(df_backtest.index, df_backtest["close"], label="Close Price", color="blue")
        buy_signals = df_backtest[df_backtest["signal"] == 1]
        sell_signals = df_backtest[df_backtest["signal"] == -1]
        ax.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="Buy")
        ax.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", label="Sell")
        ax.set_title("Trading Signals")
        ax.legend()
        st.pyplot(fig)

        # --- MACD Plot ---
        if "MACD" in df_backtest.columns and "Signal_Line" in df_backtest.columns:
            st.write("MACD Indicator")
            fig2, ax2 = plt.subplots(figsize=(12, 4))
            ax2.plot(df_backtest.index, df_backtest["MACD"], label="MACD", color="purple")
            ax2.plot(df_backtest.index, df_backtest["Signal_Line"], label="Signal Line", color="orange")
            ax2.axhline(0, color="black", linewidth=1, linestyle="--")
            ax2.legend()
            st.pyplot(fig2)

        # --- Portfolio Value Plot ---
        if "portfolio_value" in df_backtest.columns:
            st.write("Portfolio Value Over Time")
            fig3, ax3 = plt.subplots(figsize=(12, 4))
            ax3.plot(df_backtest.index, df_backtest["portfolio_value"], label="Portfolio Value", color="gold")
            ax3.set_title("Portfolio Value")
            ax3.legend()
            st.pyplot(fig3)
            st.success(f"Final Portfolio Value: ${df_backtest['portfolio_value'].iloc[-1]:,.2f}")

        # --- Display Backtest Metrics ---
        if metrics:
            st.write("Key Performance Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Return", f"{metrics.get('Total Return', 0)*100:.2f}%")
            col2.metric("CAGR", f"{metrics.get('CAGR', 0)*100:.2f}%")
            col3.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")

            col4, col5, col6 = st.columns(3)
            col4.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0)*100:.2f}%")
            col5.metric("Win Rate", f"{metrics.get('Win Rate', 0)*100:.2f}%")
            col6.metric("Number of Trades", f"{metrics.get('Number of Trades', 0)}")

        # --- Download Backtest Results ---
        csv_buffer = io.StringIO()
        df_backtest.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download Backtest Results (CSV)",
            data=csv_buffer.getvalue(),
            file_name="backtest_results.csv",
            mime="text/csv"
        )

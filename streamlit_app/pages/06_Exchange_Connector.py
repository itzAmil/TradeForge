# streamlit_app/pages/06_Exchange_Connector.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from api.exchange_api import get_all_symbols, get_current_price, fetch_ohlcv

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="🔗 Exchange Connector", layout="wide")
st.title("🔗 Exchange Connector")
st.write("Explore trading symbols, view current prices, and fetch OHLCV data from your exchange. 📈💹")

# -----------------------------
# 1. Symbol Explorer
# -----------------------------
st.header("1️⃣ Symbol Explorer")
symbols = get_all_symbols()
if symbols:
    default_index = symbols.index("BTCUSDT") if "BTCUSDT" in symbols else 0
    symbol = st.selectbox("Select Trading Symbol 🔹", symbols, index=default_index)
else:
    st.error("⚠️ Could not fetch symbols from the exchange.")
    symbol = "BTCUSDT"

# -----------------------------
# 2. Current Price Viewer
# -----------------------------
st.header("2️⃣ Current Price")
if st.button("💰 Get Current Price"):
    price = get_current_price(symbol)
    if price is not None:
        st.success(f"Current price for {symbol}: {price} USD")
    else:
        st.error("❌ Failed to fetch current price.")

# -----------------------------
# 3. OHLCV Candlestick Chart
# -----------------------------
st.header("3️⃣ OHLCV Candlestick Chart")
interval = st.selectbox("Interval ⏱️", ["1m", "5m", "15m", "1h", "4h", "1d"], index=0)
limit = st.slider("Number of Candles 📊", min_value=10, max_value=500, value=100, step=10)

if st.button("📈 Fetch OHLCV Data"):
    ohlcv = fetch_ohlcv(symbol, interval, limit)
    if ohlcv:
        df = pd.DataFrame(ohlcv)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        fig = go.Figure(data=[go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color='green',
            decreasing_line_color='red'
        )])
        fig.update_layout(
            title=f"{symbol} OHLCV ({interval}) 📊",
            xaxis_title="Time",
            yaxis_title="Price"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show table preview
        st.subheader("📋 OHLCV Data Preview")
        st.dataframe(df.head())

        # Download button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download OHLCV CSV",
            data=csv,
            file_name=f"{symbol}_{interval}_ohlcv.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ Failed to fetch OHLCV data.")

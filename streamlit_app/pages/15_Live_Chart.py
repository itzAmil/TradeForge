#streamlit_app/pages/15_Live_Chart.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import os
import sys
import importlib.util

# ------------------------------------------------------------------------------
# Ensure we can import from sql/ (project root)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # TradeForge/streamlit_app
ROOT_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".."))  # TradeForge (project root)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Dynamically import query_handler for DB access
sql_path = os.path.join(ROOT_DIR, "sql", "query_handler.py")
spec = importlib.util.spec_from_file_location("query_handler", sql_path)
query_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(query_handler)

fetch_recent_ohlcv = query_handler.fetch_recent_ohlcv
fetch_recent_predictions = query_handler.fetch_recent_predictions

# ------------------------------------------------------------------------------
# Streamlit Config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="TradeForge Live Chart", layout="wide")
st.title("📈 TradeForge Live Signal Dashboard")

# Auto-refresh every 15s
st_autorefresh(interval=15 * 1000, key="auto_refresh")

# Sidebar controls
symbol = st.sidebar.selectbox("Select Symbol", ["BTCUSDT"])
interval = st.sidebar.selectbox("Select Interval", ["1m", "5m"])
num_candles = st.sidebar.slider("Candles to Display", 20, 200, 100)

st.sidebar.markdown("---")

# ------------------------------------------------------------------------------
# Fetch OHLCV & predictions from DB (fallback CSV if DB empty)
# ------------------------------------------------------------------------------
ohlcv_df = fetch_recent_ohlcv(symbol, interval, limit=num_candles)
pred_df = fetch_recent_predictions(symbol, interval, limit=num_candles)

if ohlcv_df.empty:
    csv_path = os.path.join(ROOT_DIR, "data", "BTCUSDT_15m.csv")
    if os.path.exists(csv_path):
        ohlcv_df = pd.read_csv(csv_path).tail(num_candles)
        ohlcv_df['timestamp'] = pd.to_datetime(ohlcv_df['timestamp'])
        st.info("DB empty - using fallback CSV")
    else:
        st.warning("No data found in DB or CSV.")
        st.stop()

# Merge predictions if available
if not pred_df.empty:
    df = pd.merge(ohlcv_df, pred_df, on='timestamp', how='left')
else:
    df = ohlcv_df.copy()
    df['prediction'] = 0  # placeholder

# ------------------------------------------------------------------------------
# Plot Candlestick + RSI + Predictions
# ------------------------------------------------------------------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name="Price",
    increasing_line_color='green',
    decreasing_line_color='red'
))

# RSI line
if 'rsi' in df.columns:
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['rsi'],
        name="RSI",
        yaxis="y2",
        line=dict(color='blue', dash='dot')
    ))

# Buy/Sell markers from predictions
if 'prediction' in df.columns:
    buys = df[df['prediction'] == 1]
    sells = df[df['prediction'] == -1]

    fig.add_trace(go.Scatter(
        x=buys['timestamp'], y=buys['close'],
        mode='markers', marker=dict(symbol='triangle-up', color='lime', size=10),
        name='Buy'
    ))
    fig.add_trace(go.Scatter(
        x=sells['timestamp'], y=sells['close'],
        mode='markers', marker=dict(symbol='triangle-down', color='orange', size=10),
        name='Sell'
    ))

fig.update_layout(
    height=700,
    xaxis_rangeslider_visible=False,
    yaxis=dict(title='Price'),
    yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False),
    margin=dict(l=40, r=40, t=40, b=40)
)

# Show chart
st.plotly_chart(fig, use_container_width=True)

st.caption("Auto-refreshes every 15 seconds · Powered by TradeForge")

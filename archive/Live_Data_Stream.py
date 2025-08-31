# streamlit_app/pages/14_Live_Data_Stream.py
"""
File: streamlit_app/pages/14_Live_Data_Stream.py
Description:
Streamlit-based live data stream UI for TradeForge.
Displays real-time trade logs and model predictions from the WebSocket streamer.
"""

import os
import sys
import time
import json
import pandas as pd
import streamlit as st

# -----------------------------
# Ensure project root in sys.path (so `from streaming import websocket_streamer` works)
# -----------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -----------------------------
# Imports
# -----------------------------
from streaming import websocket_streamer
from utils.tradeforge_logger import setup_logger

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="TradeForge Live Stream", layout="wide")
st.title("Live Data Stream 📈")
st.write("Monitor live trade logs and model predictions in real-time.")

# -----------------------------
# Logger
# -----------------------------
logger = setup_logger(__name__)

# -----------------------------
# Auto-Trading Config
# -----------------------------
AUTO_TRADING_CONFIG_PATH = websocket_streamer.AUTO_TRADING_CONFIG_PATH

def set_auto_trading(enabled: bool):
    os.makedirs(os.path.dirname(AUTO_TRADING_CONFIG_PATH), exist_ok=True)
    with open(AUTO_TRADING_CONFIG_PATH, "w") as f:
        json.dump({"enabled": enabled}, f)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Configuration")

selected_symbol = st.sidebar.text_input("Symbol (e.g., BTCUSDT)", value="BTCUSDT")
selected_interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h"], index=0)
trade_quantity = st.sidebar.number_input("Trade Quantity", min_value=0.0001, value=0.001)

auto_trade = st.sidebar.checkbox(
    "Enable Auto-Trading", value=websocket_streamer.is_auto_trading_enabled()
)
set_auto_trading(auto_trade)

refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)

# -----------------------------
# Model Status
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Model Status")
if websocket_streamer.model:
    st.sidebar.success(f"Model Loaded: {websocket_streamer.model_name}")
else:
    st.sidebar.error("No model available")

# -----------------------------
# Stream Controls
# -----------------------------
st.sidebar.markdown("---")
start_button = st.sidebar.button("Start Stream")
stop_button = st.sidebar.button("Stop Stream")

if "stream_running" not in st.session_state:
    st.session_state.stream_running = False

# -----------------------------
# Start / Stop Logic
# -----------------------------
def start_stream():
    # Reconfigure the streamer and launch its singleton background thread
    websocket_streamer.SYMBOL = selected_symbol.lower()
    websocket_streamer.INTERVAL = selected_interval
    websocket_streamer.STREAM_URL = (
        f"wss://stream.binance.com:9443/ws/"
        f"{websocket_streamer.SYMBOL}@kline_{websocket_streamer.INTERVAL}"
    )
    websocket_streamer.start_stream()

if start_button:
    if not st.session_state.stream_running:
        start_stream()
        st.session_state.stream_running = True
        st.success("WebSocket stream started! ✅")
    else:
        st.warning("Stream already running! ⚠️")

if stop_button:
    # We don't kill the background thread here; we just stop auto-refreshing the UI.
    st.session_state.stream_running = False
    st.info("WebSocket stream display paused. ⏸️ (Background socket may still be connected)")

# -----------------------------
# Live Logs / Predictions
# -----------------------------
st.subheader("📜 Live Logs & Predictions")
table_placeholder = st.empty()
styled_placeholder = st.empty()

def fetch_latest_logs(limit=10) -> pd.DataFrame:
    """Fetch last N entries from websocket_streamer in a thread-safe way."""
    try:
        # Prefer the safe accessor if available
        if hasattr(websocket_streamer, "get_latest_entries"):
            entries = websocket_streamer.get_latest_entries(limit=limit)
        else:
            entries = getattr(websocket_streamer, "latest_entries", [])[-limit:]
        if not entries:
            return pd.DataFrame()

        df = pd.DataFrame(entries)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False)
        for col in ["close", "rsi", "prediction"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Round numeric columns for neat display
        for col in ["close", "rsi"]:
            if col in df.columns:
                df[col] = df[col].round(4)
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch latest logs: {e}")
        return pd.DataFrame()

def render_styled_logs(df: pd.DataFrame) -> str:
    """Render rows as emoji-styled Markdown lines."""
    if df.empty:
        return "⌛ Waiting for live logs/predictions..."
    lines = []
    for _, row in df.iterrows():
        ts = row.get("timestamp", "")
        close = row.get("close", "")
        rsi = row.get("rsi", "")
        pred = row.get("prediction", "")
        # Use simple legend: 1=BUY ✅, -1=SELL 🔻, 0/None=ℹ️
        if pred == 1:
            emoji = "✅"
        elif pred == -1:
            emoji = "🔻"
        elif pred == 0:
            emoji = "❌"
        else:
            emoji = "ℹ️"
        lines.append(f"{emoji} **{ts}** | Close: `{close}` | RSI: `{rsi}` | Prediction: `{pred}`")
    return "\n\n".join(lines)

# -----------------------------
# Display (non-blocking) + periodic rerun only when streaming
# -----------------------------
df_logs = fetch_latest_logs(limit=10)
if not df_logs.empty:
    table_placeholder.dataframe(df_logs.reset_index(drop=True))
    styled_placeholder.markdown(render_styled_logs(df_logs), unsafe_allow_html=True)
else:
    styled_placeholder.text("⌛ Waiting for live logs/predictions...")

# Auto-refresh only while streaming
if st.session_state.stream_running:
    # Sleep briefly, then rerun this script to refresh the placeholders.
    time.sleep(refresh_interval)
    # Use the stable API name if available; fall back to experimental.
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

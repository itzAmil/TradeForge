# streamlit_app/Dashboard.py
"""
TradeForge Streamlit Dashboard
------------------------------
Main landing page for the TradeForge dashboard.
Displays real-time OHLCV data from SQL or falls back to CSV if unavailable.
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime
import importlib.util

# -------------------------------
# Paths & Root (fixed to streamlit_app level)
# -------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# -------------------------------
# Import SQL Query Handler
# -------------------------------
sql_path = os.path.join(ROOT_DIR, "..", "sql", "query_handler.py")
spec = importlib.util.spec_from_file_location("query_handler", sql_path)
query_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(query_handler)
fetch_ohlcv_data = query_handler.fetch_recent_ohlcv

# -------------------------------
# Import Chart Visualizer
# -------------------------------
vis_path = os.path.join(ROOT_DIR, "pages", "14_Chart_Visualizer.py")
spec2 = importlib.util.spec_from_file_location("chart_vis", vis_path)
chart_vis = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(chart_vis)
plot_ohlcv_with_signals = chart_vis.plot_ohlcv_with_signals

# -------------------------------
# Streamlit Config
# -------------------------------
st.set_page_config(page_title="TradeForge Dashboard", layout="wide")
st.title("📊 TradeForge Live Dashboard")

# -------------------------------
# Sidebar Controls
# -------------------------------
st.sidebar.header("⚙️ Settings")
SYMBOL = st.sidebar.selectbox("Select Symbol", options=["BTCUSDT"])
INTERVAL = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"])

show_sma = st.sidebar.checkbox("Show SMA", value=True)
show_ema = st.sidebar.checkbox("Show EMA", value=True)
show_rsi = st.sidebar.checkbox("Show RSI", value=True)

# -------------------------------
# Load Chart Data (with Debug Info + auto CSV fallback)
# -------------------------------
@st.cache_data(ttl=10)
def load_chart_data(symbol, interval):
    df = pd.DataFrame()
    source = "None"

    # Try database
    try:
        df = fetch_ohlcv_data(symbol, interval)
        if df is not None and not df.empty:
            source = "Database"
    except Exception as e:
        st.sidebar.error(f"DB Error: {e}")

    # If DB empty, fallback to CSV (auto-detect)
    if df is None or df.empty:
        data_dir = os.path.join(ROOT_DIR, "..", "data")
        expected_file = f"{symbol}_{interval}.csv"
        csv_path = os.path.join(data_dir, expected_file)

        if not os.path.exists(csv_path):
            # Try to find any CSV starting with symbol_
            candidates = [f for f in os.listdir(data_dir) if f.startswith(symbol) and f.endswith(".csv")]
            if candidates:
                csv_path = os.path.join(data_dir, candidates[0])  # take first available
                st.sidebar.warning(f"⚠️ Exact file {expected_file} not found, using {candidates[0]} instead.")

        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty:
                    source = f"CSV ({os.path.basename(csv_path)})"
            except Exception as e:
                st.sidebar.error(f"CSV Error: {e}")

    # Final cleanup
    if df is not None and not df.empty:
        st.sidebar.success(f"✅ Loaded from {source} | Rows: {len(df)}")
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")
        df["signal"] = 0
    else:
        st.sidebar.error("❌ No data source found (DB/CSV)")
        df = pd.DataFrame()

    return df, source

chart_df, source_used = load_chart_data(SYMBOL, INTERVAL)

# -------------------------------
# KPI Metrics
# -------------------------------
if not chart_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    total_rows = len(chart_df)
    pnl = chart_df["close"].iloc[-1] - chart_df["close"].iloc[0]
    pnl_pct = (pnl / chart_df["close"].iloc[0]) * 100

    with col1:
        st.metric("Data Points", total_rows)
    with col2:
        st.metric("Start Close", f"{chart_df['close'].iloc[0]:.2f}")
    with col3:
        st.metric("End Close", f"{chart_df['close'].iloc[-1]:.2f}")
    with col4:
        st.metric("Change (%)", f"{pnl_pct:.2f}%")

# -------------------------------
# Dummy Portfolio (slightly improved)
# -------------------------------
if not chart_df.empty:
    portfolio = pd.DataFrame(index=chart_df["timestamp"])
    portfolio["total"] = (chart_df["close"].pct_change().fillna(0) + 1).cumprod() * 1000
else:
    portfolio = None

# -------------------------------
# Chart Section
# -------------------------------
st.subheader("📈 OHLCV Chart")
if not chart_df.empty:
    st.write(f"**Source Used:** {source_used}")
    st.dataframe(chart_df.head())  # 👀 Quick preview for debugging

    fig = plot_ohlcv_with_signals(
        chart_df,
        show_sma=show_sma,
        show_ema=show_ema,
        show_rsi=show_rsi,
        portfolio=portfolio,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.warning("⚠️ No chart data available. Please check your database or CSV fallback.")

st.markdown("---")
st.caption("Powered by TradeForge 🚀")

#streamlit_app/pages/13_Trade_Executor.py

"""
Trade Executor UI
-----------------
Streamlit-based UI for placing simulated trades (Testnet).
Reads logs from CSV and displays recent trades.
"""

import sys
import os
import pandas as pd
import streamlit as st

# -----------------------------
# Path Fix (ensure TradeForge root is in sys.path)
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.trade_executor import place_test_order, TRADE_LOG_PATH

# -----------------------------
# UI Layout
# -----------------------------
st.set_page_config(page_title="Trade Executor", page_icon="💹", layout="wide")
st.title("Trade Executor")
st.write("Place simulated trades and review trade logs.")

# -----------------------------
# Trade Input Form
# -----------------------------
with st.form("trade_form"):
    symbol = st.text_input("Trading Pair (e.g., BTCUSDT)", value="BTCUSDT")
    side = st.selectbox("Order Side", ["BUY", "SELL"])
    quantity = st.number_input("Quantity", value=0.001, format="%.6f")
    submitted = st.form_submit_button("Execute Trade")

    if submitted:
        place_test_order(symbol, side, quantity)
        st.success(f"✅ {side} order placed for {symbol} (Qty: {quantity})")

# -----------------------------
# Show Trade Log
# -----------------------------
if os.path.exists(TRADE_LOG_PATH):
    st.subheader("📄 Trade Log")
    df = pd.read_csv(TRADE_LOG_PATH, encoding="utf-8")
    st.dataframe(df.tail(10))
else:
    st.info("No trades logged yet.")

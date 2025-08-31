# streamlit_app/pages/04_SQL_Seeder.py

import os
import sys
import streamlit as st
import pandas as pd

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import functions from your script
from scripts.populate_sql_from_mongo import transfer_data, run_sql_populator, MONGO_DB, MONGO_COLLECTION

# --- Page Configuration ---
st.set_page_config(page_title="SQL Seeder", layout="wide")
st.title("🗄️ SQL Seeder")
st.write("""
Sync OHLCV data from MongoDB into your SQLite database.
Select symbols & intervals, then run the SQL populator. 🚀
""")

# --- Symbol & Interval Selection ---
symbols = st.multiselect(
    "🔹 Select symbols",
    options=["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
    default=["BTCUSDT", "ETHUSDT"]
)

intervals = st.multiselect(
    "⏱️ Select intervals",
    options=["1m", "5m", "15m"],
    default=["1m", "5m"]
)

# --- Run SQL Populator ---
if st.button("⚡ Run SQL Populator"):
    total_tables = 0
    for symbol in symbols:
        for interval in intervals:
            st.info(f"🔄 Processing {symbol} [{interval}]...")
            transfer_data(symbol, interval)
            total_tables += 1
    st.success(f"🏆 SQL Sync Complete: {total_tables} tables processed!")

# --- Display MongoDB info ---
st.write("🗃️ MongoDB Database:", MONGO_DB)
st.write("📂 MongoDB Collection:", MONGO_COLLECTION)

# streamlit_app/pages/05_MongoDB_Explorer.py

import streamlit as st
import pandas as pd
from storage import mongo_handler

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="🗄️ MongoDB Explorer", layout="wide")
st.title("🗄️ MongoDB Explorer")
st.write("Browse and download OHLCV data directly from your MongoDB instance. 📊")

# -----------------------------
# Symbol & Interval Selection
# -----------------------------
symbol_intervals = mongo_handler.get_all_symbols_and_intervals()
symbols = sorted(list(set([s for s, i in symbol_intervals])))

selected_symbol = st.selectbox("Select Symbol 🔹", symbols)
intervals_for_symbol = [i for s, i in symbol_intervals if s == selected_symbol]
selected_interval = st.selectbox("Select Interval ⏱️", intervals_for_symbol)

st.write(f"Displaying MongoDB data for **{selected_symbol}** [{selected_interval}]")

# -----------------------------
# Fetch Data
# -----------------------------
collection_name = f"{selected_symbol}_{selected_interval}"
data_cursor = mongo_handler.db[collection_name].find()
df = pd.DataFrame(list(data_cursor))

# Clean Data
if "_id" in df.columns:
    df.drop(columns=["_id"], inplace=True)

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# Display & Visualize Data
# -----------------------------
if df.empty:
    st.warning("⚠️ No data available for this selection.")
else:
    # Full Data Table
    st.subheader("📋 Full Data Table")
    st.dataframe(df)

    # Download CSV button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{selected_symbol}_{selected_interval}.csv",
        mime="text/csv"
    )

    # Basic Stats
    st.subheader("📊 Data Summary")
    st.write(df.describe(include="number"))

    # Close price chart
    if "close" in df.columns:
        st.subheader("💹 Close Price Chart")
        st.line_chart(df.set_index("timestamp")["close"])

    # Volume chart
    if "volume" in df.columns:
        st.subheader("📈 Volume Chart")
        st.bar_chart(df.set_index("timestamp")["volume"])

    # Last 10 rows
    st.subheader("🕑 Last 10 Records")
    st.write(df.tail(10))

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    ---
    Data is fetched live from your local MongoDB instance.
    All timestamps are UTC and displayed as strings for compatibility.
    """
)

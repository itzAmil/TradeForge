# streamlit_app/pages/03_Data_Preprocessor.py

import sys, os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Path fix: ensure project root is on sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml.feature_engineering import compute_technical_indicators
from ml.label_generator import generate_labels

# --- Page configuration ---
st.set_page_config(page_title="Data Preprocessor", layout="wide")
st.title("🛠️ Data Preprocessor")
st.write("Upload raw OHLCV data → compute technical indicators → generate labels → download dataset")

# --- File uploader ---
uploaded_file = st.file_uploader("📁 Upload OHLCV CSV (must have 'close' column)", type=["csv"])

# --- Parameters ---
threshold = st.number_input("⚖️ Return Threshold (e.g., 0.002 = 0.2%)", value=0.002, format="%.5f")
future_window = st.number_input("⏩ Future Window (steps ahead)", value=5, min_value=1, step=1)

if uploaded_file:
    df = pd.read_csv(uploaded_file).dropna()

    if "close" not in df.columns:
        st.error("❌ CSV must contain a 'close' column.")
    else:
        try:
            # --- Compute indicators + labels ---
            df = compute_technical_indicators(df)
            df = generate_labels(df, threshold=threshold, future_window=future_window)

            st.subheader("📊 Preview of Processed Data")
            st.dataframe(df.head(20))

            # --- Download CSV ---
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="💾 Download Processed & Labeled CSV",
                data=csv,
                file_name="processed_labeled_dataset.csv",
                mime="text/csv",
            )

            # --- Visualization ---
            st.subheader("📈 Price Chart with Labels")

            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df["close"], mode="lines", name="Close Price"))

            buys = df[df["label"] == 1]
            sells = df[df["label"] == -1]

            fig.add_trace(go.Scatter(
                x=buys.index, y=buys["close"],
                mode="markers", marker=dict(color="green", size=8, symbol="triangle-up"),
                name="Buy Signal"
            ))
            fig.add_trace(go.Scatter(
                x=sells.index, y=sells["close"],
                mode="markers", marker=dict(color="red", size=8, symbol="triangle-down"),
                name="Sell Signal"
            ))

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Processing failed: {e}")

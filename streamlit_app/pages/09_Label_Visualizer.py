# streamlit_app/pages/09_Label_Visualizer.py

import sys, os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Path fix: ensure project root is on sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.label_generator import generate_labels

# --- Streamlit Page Config ---
st.set_page_config(page_title="📊 Label Visualizer", layout="wide")
st.title("📊 Label Visualizer")
st.write("Upload OHLCV data → apply signal labels → download labeled dataset ✅")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload OHLCV CSV (must have 'close' column)", type=["csv"])

# --- Parameters ---
threshold = st.number_input("Return Threshold (e.g., 0.002 = 0.2%)", value=0.002, format="%.5f")
future_window = st.number_input("Future Window (steps ahead)", value=5, min_value=1, step=1)

if uploaded_file:
    df = pd.read_csv(uploaded_file).dropna()

    if "close" not in df.columns:
        st.error("❌ CSV must contain a 'close' column.")
    else:
        # --- Generate labels ---
        df_labeled = generate_labels(df, threshold=threshold, future_window=future_window)

        st.subheader("📝 Preview of Labeled Data")
        st.dataframe(df_labeled.head(20))

        # --- Download CSV ---
        csv = df_labeled.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download Labeled CSV",
            data=csv,
            file_name="labeled_dataset.csv",
            mime="text/csv",
        )

        # --- Visualization ---
        st.subheader("📈 Price Chart with Buy/Sell Signals")
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df_labeled["close"], mode="lines", name="Close Price"))

        # Add buy/sell markers
        buys = df_labeled[df_labeled["label"] == 1]
        sells = df_labeled[df_labeled["label"] == -1]

        fig.add_trace(go.Scatter(
            x=buys.index, y=buys["close"],
            mode="markers", marker=dict(color="green", size=8, symbol="triangle-up"),
            name="Buy"
        ))
        fig.add_trace(go.Scatter(
            x=sells.index, y=sells["close"],
            mode="markers", marker=dict(color="red", size=8, symbol="triangle-down"),
            name="Sell"
        ))

        st.plotly_chart(fig, use_container_width=True)
